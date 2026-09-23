"""Identity-only agreement pointers; the referenced Markdown owns its wording."""
DOCUMENTS = {'product_design': 'product-design.md', 'architecture': 'architecture.md'}


def catalog(state):
    result = {}
    for kind, path in DOCUMENTS.items():
        for group in ('decisions', 'rules'):
            for row in (state.get(kind) or {}).get(group, []):
                if row.get('id'):
                    key = path+'::'+row['id']
                    if key in result: raise ValueError('Ambiguous agreement identity: '+key)
                    section = 'product-rules' if group == 'rules' else ('design-decisions' if kind == 'product_design' else 'architecture-decisions')
                    if group == 'decisions' and row.get('status') in {'superseded', 'rejected'}: section = 'decision-history'
                    if group == 'decisions' and row.get('status') == 'proposed': section = 'proposed-decisions'
                    result[key] = (row, path+'#'+section)
    return result


def pointers(state):
    for kind, path in DOCUMENTS.items():
        for group, rows in (state.get(kind) or {}).items():
            if not isinstance(rows, list): continue
            for row in rows:
                if isinstance(row, dict) and 'agreement_refs' in row:
                    yield path+' '+str(row.get('id', group)), row['agreement_refs'], True
    for row in state.get('product_backlog', []):
        yield 'backlog/'+row['id']+'.md', row.get('references', []), False
    for row in state.get('project', {}).get('collaboration', {}).get('highlights', []):
        yield 'constitution.md highlight', row.get('references', []), False


def validate(state, error):
    try: known = catalog(state)
    except ValueError as exc: raise error(str(exc))
    for owner, refs, strict in pointers(state):
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            raise error('Agreement references must be text lists: '+owner)
        for ref in refs:
            if strict or ('::' in ref and ref.split('::', 1)[0] in DOCUMENTS.values()):
                if ref not in known: raise error('Unknown agreement reference: '+ref)


def stale(state):
    known = catalog(state)
    for owner, refs, strict in pointers(state):
        for ref in refs:
            if ref in known and known[ref][0].get('status') in {'superseded', 'rejected'}:
                yield owner, ref
