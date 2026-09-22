"""Optional authored design records, independent of delivery scheduling."""
import copy

DOCUMENTS = {'product_design': 'product-design.md', 'architecture': 'architecture.md'}
COMMON = {'purpose', 'status', 'scope', 'exclusions', 'alternatives', 'decisions',
          'open_questions', 'references', 'updated_at', 'changes'}
FIELDS = {
    'product_design': COMMON | {'journeys', 'screens', 'states', 'accessibility'},
    'architecture': COMMON | {'constraints', 'components', 'data', 'integrations', 'operations'},
}
ROWS = {'alternatives', 'decisions', 'open_questions', 'journeys', 'screens',
        'states', 'accessibility', 'components', 'data', 'integrations', 'operations'}
KNOWLEDGE = {'proposed', 'confirmed', 'decided', 'superseded', 'rejected'}


def validate(kind, document, error):
    if not isinstance(document, dict) or not isinstance(document.get('purpose'), str) or not document['purpose'].strip():
        raise error('Design documents require a meaningful purpose.')
    if set(document) - FIELDS[kind]:
        raise error('Unsupported design fields: ' + ', '.join(sorted(set(document) - FIELDS[kind])))
    if document.get('status', 'draft') not in {'draft', 'in-review', 'agreed', 'superseded'}:
        raise error('Invalid design document status.')
    for field in ROWS & document.keys():
        rows = document[field]
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise error(field + ' must contain structured rows.')
        for row in rows:
            if row.get('status') is not None and row['status'] not in KNOWLEDGE:
                raise error('Invalid design knowledge status.')
    decisions = document.get('decisions', [])
    ids = [row.get('id') for row in decisions]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(ids) != len(set(ids)):
        raise error('Design decisions need distinct local IDs.')
    for row in decisions:
        if not row.get('decision') or not row.get('scope') or row.get('status') not in KNOWLEDGE:
            raise error('Design decisions need decision, scope and knowledge status.')
        if row['status'] in {'confirmed', 'decided', 'superseded'}:
            if row.get('basis') not in {'user-definition', 'user-confirmation', 'delegated', 'technical-discretion'} or not row.get('source'):
                raise error('Settled design decisions require a basis and actual source.')
        if row.get('supersedes') and row['supersedes'] not in ids:
            raise error('A superseded design decision must exist in the same document.')
    for row in document.get('open_questions', []):
        if not row.get('question') or row.get('timing') not in {'now', 'later', 'investigate'}:
            raise error('Design questions need question and timing: now, later or investigate.')
        if row['timing'] == 'later' and not row.get('revisit_when'):
            raise error('Deferred questions need a revisit point.')
    if 'references' in document and (not isinstance(document['references'], list) or any(not isinstance(r, str) for r in document['references'])):
        raise error('References must be source strings.')


def update(state, kind, request, now, error):
    fields = request.get('document')
    if not isinstance(fields, dict) or not fields or set(fields) - (FIELDS[kind] - {'updated_at', 'changes'}):
        raise error('Provide supported design document fields; history is managed by the writer.')
    previous = state.get(kind) or {}
    if 'decisions' in fields and isinstance(fields['decisions'], list):
        old = {row['id']: row for row in previous.get('decisions', [])}
        new = {row.get('id'): row for row in fields['decisions'] if isinstance(row, dict)}
        if set(old) - set(new):
            raise error('Preserve existing design decisions; supersede them explicitly instead of deleting history.')
        for ident, row in old.items():
            if row['status'] in {'confirmed', 'decided', 'superseded'}:
                for key in ('decision', 'scope', 'basis', 'source'):
                    if new[ident].get(key) != row.get(key):
                        raise error('Preserve the settled decision and add a sourced replacement with supersedes.')
                if new[ident].get('status') not in {row['status'], 'superseded'}:
                    raise error('A settled decision can only retain its status or be superseded.')
    document = copy.deepcopy(previous)
    document.update(copy.deepcopy(fields))
    document.setdefault('status', 'draft')
    document['updated_at'] = now
    document.setdefault('changes', []).append({'at': now, 'change': request['purpose'], 'source': request.get('provenance', 'Not recorded')})
    validate(kind, document, error)
    state[kind] = document
