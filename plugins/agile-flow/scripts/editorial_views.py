"""Generated editorial indexes. The domain engine owns effective delivery states."""
try:
    from . import editorial_codec as codec, legacy_records as engine, iterative_lifecycle as lifecycle
    from .release_store import iteration_path
    from . import agreement_references as agreements
except ImportError:
    import editorial_codec as codec, legacy_records as engine, iterative_lifecycle as lifecycle
    from release_store import iteration_path
    import agreement_references as agreements


def generate(store,state,available):
    project=state['project']; needs=[]; completed=[]
    for row in sorted(state['product_backlog'],key=lambda r:(r.get('order') or float('inf'),r['id'])):
        item={'order':row.get('order','Unranked'), 'document':f"[{row['id']} — {row['purpose']}]({row['id']}.md)",
              'value':row.get('value','Not recorded'), 'state':row['state'], 'target_release':row.get('target_release') or 'Unassigned'}
        if row['state'] in {'closed','canceled','retired','done'}:
            completed.append({'document':item['document'],'state':row['state'],'outcome':row.get('outcome','Not recorded')})
        else:needs.append(item)
    backlog={'needs':needs,'completed':completed}
    if project.get('priority_rationale'):backlog['priority_rationale']=project['priority_rationale']
    observed=engine.inspect_state(store,state)
    current=[]
    for release in state['releases']:
        if release['status'] in {'released','canceled'}:continue
        iterations=[it for it in state['iterations'] if it['release_id']==release['id'] and it['state'] not in {'closed','canceled'}]
        for it in iterations or [None]:
            current.append({'release':f"[{release['id']}](release/{release['id']}/release-{release['id'][1:]}.md)",
                            'objective':release['objective'],
                            'iteration':f"[{it['id']}]({iteration_path(it)}/sprint-planning.md)" if it else 'Not planned',
                            'goal':it['goal'] if it else 'Not recorded','status':it['state'] if it else release['status']})
    summary={'purpose':project['purpose'],'current':current,'next_step':project['next_step'],
             'deliveries':[{'id':i['id'],'development':i['states']['development'],'verification':i['effective_verification'],
                            'acceptance':i['effective_acceptance'],'limit':i.get('limitations','Not recorded')} for i in observed['increments']],
             'pending':[{'item':b['id'],'impact':b['condition'],'resolution':b['resolution_requirement']} for b in state['blockers'] if b['state']=='open']+
                       [{'item':q,'impact':'Not recorded','resolution':'User clarification'} for q in project.get('open_questions',[])]}
    if lifecycle.enabled(state):
        summary['lifecycle_status'] = [{'release': r['id'], 'commitment': 'Agreed' if r.get('commitment') else 'Draft',
            'fulfillment': lifecycle.effective_fulfillment(store,state,r,engine), 'publication': r['status']} for r in state['releases']]
    summary['deferred'] = []; summary['investigate'] = []
    summary['reconciliation'] = []
    user_question_count = len(project.get('open_questions', []))
    if project.get('collaboration'): summary['collaboration'] = {k: v for k, v in project['collaboration'].items() if k in {'focus', 'level'}}
    dates = [a['at'] for a in project.get('amendments', []) if a.get('at')]
    dates += [d['at'] for d in state['decisions'] if d.get('at')]
    dates += [h['at'] for h in state.get('history', []) if h.get('at')]
    for group in ('product_backlog', 'releases', 'iterations'):
        dates += [c['at'] for r in state.get(group, []) for c in r.get('changes', []) if c.get('at')]
    for kind, label, path in [('product_design', 'Product design', 'product-design.md'), ('architecture', 'Architecture', 'architecture.md')]:
        document = state.get(kind) or {}
        if document.get('updated_at'): dates.append(document['updated_at'])
        link = '['+label+']('+path+')'
        for row in document.get('reconciliation', []):
            if row['status'] == 'resolved': continue
            group = 'deferred' if row['status'] == 'deferred' else 'reconciliation'
            summary[group].append({'item': row['document']+' — '+link, 'impact': row['reason'], 'resolution': row.get('revisit_when') or 'Reconcile affected content within the current mandate'})
        for row in document.get('open_questions', []):
            if row.get('status') == 'resolved': continue
            group = {'now': 'pending', 'later': 'deferred', 'investigate': 'investigate'}[row['timing']]
            if group == 'pending': user_question_count += 1
            summary[group].append({'item': row['question']+' — ['+label+']('+path+')',
                                   'impact': row.get('impact', 'Not recorded'),
                                   'resolution': row.get('revisit_when') or ('Agent investigation' if group == 'investigate' else 'User clarification')})
    # Relevance is authored by the agent; indexes do not select "important" agreements.
    collaboration = project.get('collaboration', {})
    if collaboration.get('synthesis'): summary['synthesis'] = collaboration['synthesis']
    if collaboration.get('highlights'): summary['highlights'] = collaboration['highlights']
    # Inventory proposals by source collection rather than copying their full wording.
    proposal_groups = []
    groups = [('constitution.md', 'Product definition', 'proposals', project.get('proposals', []))]
    for kind, path in [('product_design', 'product-design.md'), ('architecture', 'architecture.md')]:
        for field, rows in (state.get(kind) or {}).items():
            if isinstance(rows, list) and field not in {'changes', 'open_questions', 'reconciliation'}:
                groups.append((path, field.replace('_', ' ').capitalize(), field,
                               [r for r in rows if isinstance(r, dict) and r.get('status') == 'proposed' and r.get('disposition','current') == 'current']))
    for path, label, field, rows in groups:
        if rows:
            proposal_groups.append({'item': '['+label+']('+path+')', 'impact': str(len(rows))+' pending',
                                    'resolution': 'Review in the source document'})
    summary['proposals'] = proposal_groups
    for kind, path in [('product_design','product-design.md'),('architecture','architecture.md')]:
        retained=[r for r in (state.get(kind) or {}).get('alternatives',[]) if r.get('disposition') in {'fallback','deferred'} and r.get('status') not in {'rejected','superseded'}]
        if retained:
            summary['deferred'].append({'item':'[Retained alternatives]('+path+')','impact':str(len(retained))+' deferred or fallback options; not current choices','resolution':'See scoped revisit points in the source document'})
    for owner, ref in agreements.stale(state):
        summary['reconciliation'].append({'item': owner, 'impact': 'References a historical agreement: '+ref, 'resolution': 'Review applicability; do not silently substitute a new agreement'})
    if dates:
        summary['updated_at'] = max(dates)
    backlog_dates=[c['at'] for r in state.get('product_backlog',[]) for c in r.get('changes',[]) if c.get('at')]
    backlog_dates += [h['at'] for h in state.get('history',[]) if h.get('at')]
    if backlog_dates: backlog['updated_at'] = max(backlog_dates)
    summary['can_continue'] = project.get('collaboration', {}).get('can_continue') or ('Investigate: '+ '; '.join(r['item'] for r in summary['investigate']) if summary['investigate'] else 'No independent action recorded')
    summary['needed_from_user'] = 'See the pending user choices above' if user_question_count else 'No immediate user decision recorded'
    git=store.git.status()
    if git['available']:
        summary['git']=[{'branch':git['branch'] or 'Detached HEAD','commit':git['head'] or 'No commits',
                         'changes':git['changes'] or 'No changes observed before this refresh',
                         'policy':project.get('git_policy',{}).get('commits','Not agreed')}]
    result={}
    for path,kind,body,title in [('summary.md','summary',summary,'Current situation'),('backlog/product-backlog.md','product_backlog',backlog,'Product backlog')]:
        result[path]=codec.render(kind,project['name']+' — '+title,body,document_path=path,available=available,links={ref: target for ref, (_, target) in agreements.catalog(state).items()})[0]
    return result
