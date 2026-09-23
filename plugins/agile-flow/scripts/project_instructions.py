"""Preview and maintain the plugin-owned block in a product's AGENTS.md."""
from contextlib import contextmanager
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import uuid

TEMPLATE = Path(__file__).resolve().parents[1] / 'templates' / 'project-agents.md'
BEGIN = b'<!-- agile-flow:begin'
END = b'<!-- agile-flow:end -->'
BLOCK = re.compile(rb'<!-- agile-flow:begin version=(\d+) sha256=([0-9a-f]{64}) -->\n(.*?)<!-- agile-flow:end -->', re.S)
TEMPLATE_VERSION = 1


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read_regular(path):
    if path.is_symlink():
        raise ValueError(f'Refusing symlink: {path}')
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f'Expected regular file: {path}')
    return path.read_bytes()


def preview(root, template=None):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Product root must be a directory.')
    current = read_regular(root / 'AGENTS.md')
    override = read_regular(root / 'AGENTS.override.md')
    body = (template or TEMPLATE).read_bytes()
    body.decode('utf-8')
    if not body.endswith(b'\n'):
        body += b'\n'
    wanted = (f'<!-- agile-flow:begin version={TEMPLATE_VERSION} sha256={digest(body)} -->\n'.encode()
              + body + END)
    fingerprint = digest(json.dumps({
        'root': str(root), 'agents': None if current is None else digest(current),
        'override': None if override is None else digest(override), 'template': digest(wanted),
    }, sort_keys=True).encode())
    original = current or b''
    original.decode('utf-8')
    matches = list(BLOCK.finditer(original))
    issues = []
    if override and override.strip():
        issues.append('AGENTS.override.md takes precedence; reconcile project instructions explicitly before applying.')
    if original.count(BEGIN) != len(matches) or original.count(END) != len(matches) or len(matches) > 1:
        issues.append('Ambiguous or malformed managed block; preserve and reconcile it manually.')
    proposed = original
    if not issues and matches:
        match = matches[0]
        if int(match[1]) > TEMPLATE_VERSION:
            issues.append('Managed block is newer than this plugin template; refusing downgrade.')
        elif digest(match[3]).encode() != match[2]:
            issues.append('Managed block has manual edits; review and preserve them before reconciliation.')
        else:
            proposed = original[:match.start()] + wanted + original[match.end():]
    elif not issues:
        separator = b'' if not original else (b'\n' if original.endswith(b'\n') else b'\n\n')
        proposed = original + separator + wanted + b'\n'
    result = {
        'status': 'conflict' if issues else 'ok', 'root': str(root),
        'instruction_status': 'conflict' if issues else ('current' if proposed == original else ('missing' if not matches else 'outdated')),
        'expected_source_fingerprint': fingerprint, 'template_version': TEMPLATE_VERSION,
        'changed': proposed != original, 'issues': issues,
        'diff': ''.join(difflib.unified_diff(original.decode().splitlines(True), proposed.decode().splitlines(True),
                                            fromfile='AGENTS.md (current)', tofile='AGENTS.md (proposed)')),
        'loading_note': 'Read the resulting file explicitly in the current task. Verify instruction discovery in a fresh run; nested instructions and overrides may affect precedence.',
    }
    return result, current, proposed


@contextmanager
def directory_lock(root):
    fd = os.open(root, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield fd
    finally:
        os.close(fd)


def apply(root, request, template=None):
    if not isinstance(request.get('authorization_source'), str) or not request['authorization_source'].strip():
        raise ValueError('Provide the existing user authorization_source for project instruction setup or update.')
    root = Path(root).resolve(strict=True)
    # Cooperative writers lock the directory itself; preview creates no lock file.
    with directory_lock(root) as lock:
        result, current, proposed = preview(root, template)
        if result['status'] == 'conflict':
            return result
        if request.get('expected_source_fingerprint') != result['expected_source_fingerprint']:
            return {**result, 'status': 'conflict', 'issues': ['Instruction source or template changed; preview again.']}
        if not result['changed']:
            return {**result, 'status': 'unchanged'}
        backup = root
        for component in ('.agile-flow', '.internal', 'local', 'backups', 'instructions'):
            backup = backup / component
            if backup.is_symlink():
                raise ValueError(f'Refusing symlink backup directory: {backup}')
            backup.mkdir(exist_ok=True)
        backup = backup / uuid.uuid4().hex
        backup.mkdir()
        if current is not None:
            (backup / 'AGENTS.md').write_bytes(current)
        (backup / 'source.json').write_text(json.dumps({
            'existed': current is not None, 'source_fingerprint': result['expected_source_fingerprint'],
            'authorization_source': request['authorization_source'], 'template_version': TEMPLATE_VERSION,
        }, indent=2) + '\n')
        fd, name = tempfile.mkstemp(prefix='.agile-flow-agents-', dir=root)
        try:
            with os.fdopen(fd, 'wb') as stream:
                os.fchmod(stream.fileno(), (root / 'AGENTS.md').stat().st_mode & 0o777 if current is not None else 0o644)
                stream.write(proposed)
                stream.flush()
                os.fsync(stream.fileno())
            check, _, _ = preview(root, template)
            if check['expected_source_fingerprint'] != result['expected_source_fingerprint']:
                return {**result, 'status': 'conflict', 'backup': str(backup), 'issues': ['Concurrent edit detected; preview again.']}
            os.replace(name, root / 'AGENTS.md')
            os.fsync(lock)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        return {**result, 'status': 'applied', 'backup': str(backup)}
