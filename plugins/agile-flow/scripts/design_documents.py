"""Optional authored design records, independent of delivery scheduling."""
import copy

DOCUMENTS = {'product_design': 'product-design.md', 'architecture': 'architecture.md'}
COMMON = {'purpose', 'status', 'scope', 'exclusions', 'alternatives', 'decisions',
          'open_questions', 'references', 'updated_at', 'changes', 'reconciliation'}
FIELDS = {
    'product_design': COMMON | {'journeys', 'screens', 'states', 'accessibility', 'rules', 'examples'},
    'architecture': COMMON | {'constraints', 'components', 'data', 'integrations', 'operations'},
}
ROWS = {'alternatives', 'decisions', 'open_questions', 'journeys', 'screens',
        'states', 'accessibility', 'components', 'data', 'integrations', 'operations',
        'rules', 'examples', 'reconciliation'}
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
        named = [r['id'] for r in rows if 'id' in r]
        if any(not isinstance(i, str) or not i.strip() for i in named) or len(set(named)) != len(named):
            raise error('Record IDs must be nonempty and unique within their collection.')
        for row in rows:
            allowed = {'open', 'resolved', 'deferred'} if field in {'open_questions', 'reconciliation'} else KNOWLEDGE
            if row.get('status') is not None and row['status'] not in allowed:
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
    for row in decisions:
        seen = {row['id']}; target = row.get('supersedes')
        by_id = {r['id']: r for r in decisions}
        while target:
            if target in seen: raise error('Decision supersession cannot contain cycles.')
            seen.add(target); target = by_id[target].get('supersedes')
        if not isinstance(row.get('retained_ids', []), list) or any(i not in by_id for i in row.get('retained_ids', [])):
            raise error('Retained agreements must reference decisions in the same document.')
    for row in document.get('reconciliation', []):
        if not row.get('document') or not row.get('reason') or row.get('status') not in {'open', 'resolved', 'deferred'}:
            raise error('Reconciliation requires document, reason and status.')
        if row['status'] == 'resolved' and (not row.get('resolution') or not row.get('source')):
            raise error('Resolved reconciliation requires evidence and source.')
        if row['status'] == 'deferred' and not row.get('revisit_when'):
            raise error('Deferred reconciliation requires a revisit point.')
    for row in document.get('open_questions', []):
        if not row.get('question') or row.get('timing') not in {'now', 'later', 'investigate'}:
            raise error('Design questions need question and timing: now, later or investigate.')
        if row.get('status') == 'resolved' and (not row.get('resolution') or not row.get('source')):
            raise error('Resolved questions require an answer and source.')
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


def refine(state, request, now, error):
    """Apply a set of ID-addressed edits atomically, preserving unrelated rows."""
    edits = request.get('edits')
    if not isinstance(edits, list) or not edits or not request.get('provenance'):
        raise error('Refinement requires edits and an actual provenance source.')
    working = copy.deepcopy(state)
    changed = {}
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) - {'document', 'collection', 'action', 'id', 'record', 'match'}:
            raise error('Unsupported refinement fields.')
        kind, field, action = (edit.get(k) for k in ('document', 'collection', 'action'))
        if kind not in DOCUMENTS or field not in ROWS & FIELDS[kind] or not working.get(kind):
            raise error('Refinement needs an existing design document and supported collection.')
        changed.setdefault(kind, []).append(str(field)+'/'+str(edit.get('id'))+': '+str(action))
        document = working[kind]
        rows = copy.deepcopy(document.get(field, []))
        ident = edit.get('id')
        if not isinstance(ident, str) or not ident.strip(): raise error('Refinement requires a stable record ID.')
        matches = [i for i, r in enumerate(rows) if r.get('id') == ident]
        record = copy.deepcopy(edit.get('record', {}))
        if not isinstance(record, dict): raise error('Record must be an object.')
        if action == 'add':
            if matches or record.get('id', ident) != ident: raise error('Record ID already exists or differs.')
            rows.append({**record, 'id': ident})
        elif action == 'identify':
            # Exact legacy row matching avoids ambiguous positions or silent identity assignment.
            matches = [i for i, r in enumerate(rows) if r == edit.get('match') and 'id' not in r]
            if any(r.get('id') == ident for r in rows) or len(matches) != 1 or record:
                raise error('Identify requires one exact unnamed legacy row and a new ID.')
            rows[matches[0]]['id'] = ident
        else:
            if len(matches) != 1: raise error('Unknown record ID; identify legacy rows explicitly first.')
            index = matches[0]; old = rows[index]
            if record.get('id', ident) != ident and action != 'supersede': raise error('Record identity cannot change.')
            if action == 'supersede':
                if field != 'decisions' or old.get('status') not in {'confirmed', 'decided'}:
                    raise error('Supersede requires an active settled decision.')
                new_id = record.get('id')
                if not new_id or any(r.get('id') == new_id for r in rows): raise error('Replacement needs a new ID.')
                if record.get('status') not in {'confirmed', 'decided'}: raise error('Replacement must be settled and sourced.')
                old['status'] = 'superseded'
                rows.append({**record, 'supersedes': ident})
            else:
                if action not in {'update', 'resolve', 'defer', 'adopt', 'reject'}: raise error('Unknown refinement action.')
                if action in {'resolve', 'defer'} and field not in {'open_questions', 'reconciliation'}:
                    raise error('Resolve and defer apply only to questions or reconciliation.')
                if action in {'adopt', 'reject'}:
                    if field in {'open_questions', 'reconciliation'} or old.get('status') != 'proposed':
                        raise error('Adopt and reject require a pending proposal.')
                    record.update(status='decided' if action == 'adopt' else 'rejected', source=request['provenance'])
                    if action == 'adopt' and record.get('basis') not in {'user-definition', 'user-confirmation', 'delegated', 'technical-discretion'}:
                        raise error('Adoption requires a decision basis.')
                if action == 'resolve': record.update(status='resolved', source=request['provenance'])
                if action == 'defer':
                    record['status'] = 'deferred'
                    if field == 'open_questions': record['timing'] = 'later'
                if field == 'decisions' and old.get('status') in {'confirmed', 'decided', 'superseded'}:
                    raise error('Use supersede for a settled decision; preserve its original meaning.')
                rows[index] = {**old, **record}
        update(working, kind, {**request, 'document': {field: rows}}, now, error)
    for kind, targets in changed.items():
        working[kind]['changes'] = copy.deepcopy(state[kind].get('changes', [])) + [{
            'at': now, 'change': request['purpose']+' — '+ '; '.join(targets), 'source': request['provenance']}]
    state.clear(); state.update(working)
