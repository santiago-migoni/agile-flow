"""Generated editorial indexes. The domain engine owns effective delivery states."""
try:
    from . import editorial_codec as codec, legacy_records as engine
    from .release_store import iteration_path
except ImportError:
    import editorial_codec as codec, legacy_records as engine
    from release_store import iteration_path


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
    summary['deferred'] = []; summary['investigate'] = []
    summary['proposals'] = []; summary['agreements'] = []; summary['reconciliation'] = []
    if project.get('collaboration'): summary['collaboration'] = project['collaboration']
    dates = [a['at'] for a in project.get('amendments', []) if a.get('at')]
    dates += [d['at'] for d in state['decisions'] if d.get('at')]
    dates += [h['at'] for h in state.get('history', []) if h.get('at')]
    for group in ('product_backlog', 'releases', 'iterations'):
        dates += [c['at'] for r in state.get(group, []) for c in r.get('changes', []) if c.get('at')]
    user_questions = list(project.get('open_questions', []))
    superseded = {r.get('supersedes') for r in state['decisions'] if r.get('supersedes')}
    for agreement in project.get('agreements', []):
        if isinstance(agreement, dict):
            if agreement.get('status') in {'superseded', 'rejected'}: continue
            wording = agreement.get('agreement', agreement.get('summary', agreement.get('decision', 'Not recorded')))
            scope, source = agreement.get('scope', 'Project'), agreement.get('source', 'Not recorded')
        else: wording, scope, source = agreement, 'Project', 'Not recorded'
        summary['agreements'].append({'item': str(wording)+' — [Constitution](constitution.md)', 'scope': scope, 'source': source})
    for decision in state['decisions']:
        if decision.get('kind') != 'product' or decision['id'] in superseded: continue
        summary['agreements'].append({'item': decision.get('reason', decision['id'])+' — [Constitution](constitution.md)',
                                     'scope': decision.get('scope', 'Project'), 'source': decision.get('source', 'Not recorded')})
    for proposal in project.get('proposals', []):
        summary['proposals'].append({'item': proposal.get('statement', str(proposal)) if isinstance(proposal, dict) else proposal,
                                     'impact': 'Product definition', 'resolution': 'Evaluate within the current mandate'})
    for kind, label, path in [('product_design', 'Product design', 'product-design.md'), ('architecture', 'Architecture', 'architecture.md')]:
        document = state.get(kind) or {}
        if document.get('updated_at'): dates.append(document['updated_at'])
        link = '['+label+']('+path+')'
        for collection in ('decisions', 'alternatives', 'journeys', 'screens', 'states', 'accessibility', 'components', 'data', 'integrations', 'operations', 'rules', 'examples'):
            for row in document.get(collection, []):
                description = next((row[k] for k in ('decision', 'rule', 'option', 'outcome', 'screen', 'behavior', 'component', 'data', 'system', 'approach', 'example') if row.get(k)), row.get('id', collection))
                if row.get('status') == 'proposed':
                    summary['proposals'].append({'item': str(description)+' — '+link, 'impact': row.get('scope', row.get('topic', collection)), 'resolution': 'Evaluate; no agreement or execution authority implied'})
                elif collection == 'decisions' and row.get('status') in {'confirmed', 'decided'}:
                    summary['agreements'].append({'item': str(description)+' — '+link, 'scope': row['scope'], 'source': row['source']})
        for row in document.get('reconciliation', []):
            if row['status'] == 'resolved': continue
            group = 'deferred' if row['status'] == 'deferred' else 'reconciliation'
            summary[group].append({'item': row['document']+' — '+link, 'impact': row['reason'], 'resolution': row.get('revisit_when') or 'Reconcile affected content within the current mandate'})
        for row in document.get('open_questions', []):
            if row.get('status') == 'resolved': continue
            group = {'now': 'pending', 'later': 'deferred', 'investigate': 'investigate'}[row['timing']]
            if group == 'pending': user_questions.append(row['question'])
            summary[group].append({'item': row['question']+' — ['+label+']('+path+')',
                                   'impact': row.get('impact', 'Not recorded'),
                                   'resolution': row.get('revisit_when') or ('Agent investigation' if group == 'investigate' else 'User clarification')})
    if dates: summary['updated_at'] = max(dates)
    summary['needed_from_user'] = '; '.join(str(q) for q in user_questions) or 'No immediate user decision recorded'
    summary['can_continue'] = project.get('collaboration', {}).get('can_continue') or ('Investigate: '+ '; '.join(r['item'] for r in summary['investigate']) if summary['investigate'] else 'No independent action recorded')
    git=store.git.status()
    if git['available']:
        summary['git']=[{'branch':git['branch'] or 'Detached HEAD','commit':git['head'] or 'No commits',
                         'changes':git['changes'] or 'No changes observed before this refresh',
                         'policy':project.get('git_policy',{}).get('commits','Not agreed')}]
    result={}
    for path,kind,body,title in [('summary.md','summary',summary,'Current situation'),('backlog/product-backlog.md','product_backlog',backlog,'Product backlog')]:
        result[path]=codec.render(kind,project['name']+' — '+title,body,document_path=path,available=available)[0]
    return result
