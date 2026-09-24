#!/usr/bin/env python3
"""Document-centered Agile Flow command line. Legacy migration is explicit."""
import argparse
import json
from pathlib import Path
import sys

try:
    from . import project_instructions, iterative_lifecycle
except ImportError:
    import project_instructions, iterative_lifecycle

try:
    from .clean_store import CleanStore as DocumentStore, engine
except ImportError:
    from clean_store import CleanStore as DocumentStore, engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='Explicit product checkout root.')
    parser.add_argument('--request', help='JSON request file; mutations otherwise read stdin.')
    parser.add_argument('command', choices=['inspect', 'validate', 'mutate', 'render', 'recover', 'migrate', 'git-status', 'git-preview', 'git-commit', 'git-init', 'instructions', 'lifecycle'])
    parser.add_argument('--force', action='store_true', help='Back up edited generated indexes before regenerating.')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='Read-only migration or instruction preview (default).')
    mode.add_argument('--apply', action='store_true', help='Apply migration or instructions with a reviewed source fingerprint.')
    args = parser.parse_args()
    store = DocumentStore(args.root)
    try:
        request = {}
        if args.request:
            request = json.loads(Path(args.request).read_text())
        elif args.command in {'mutate','git-preview','git-commit','git-init'} or (args.command in {'migrate', 'instructions', 'lifecycle'} and args.apply):
            request = json.loads(sys.stdin.read())
        if not isinstance(request, dict): raise ValueError('Request must be an object.')
        if args.command == 'lifecycle':
            result = iterative_lifecycle.adopt(store, request) if args.apply else iterative_lifecycle.preview(store)
        elif args.command == 'instructions':
            result = project_instructions.apply(args.root, request) if args.apply else project_instructions.preview(args.root)[0]
        elif args.command == 'git-status': result = {'status':'ok',**store.git.status()}
        elif args.command == 'git-preview':
            result = store.git_preview(request)
        elif args.command == 'git-commit':
            result=store.git_commit(request)
        elif args.command == 'git-init': result=store.git.initialize(request)
        elif args.command == 'inspect': result = store.inspect()
        elif args.command == 'validate':
            observed = store.inspect()
            result = engine.response('ok', revision=observed['revision'], document_changes=observed['document_changes'])
        elif args.command == 'render': result = store.render(args.force)
        elif args.command == 'recover': result = store.recover()
        elif args.command == 'migrate': result = store.migrate(args.apply, request)
        else: result = store.transaction(request)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result['status'] in {'failed', 'conflict'}: sys.exit(1)
    except (engine.RecordError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps(engine.response('failed', errors=[str(error)]), ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
