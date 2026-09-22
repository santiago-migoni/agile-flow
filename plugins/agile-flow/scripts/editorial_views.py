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
    git=store.git.status()
    if git['available']:
        summary['git']=[{'branch':git['branch'] or 'Detached HEAD','commit':git['head'] or 'No commits',
                         'changes':git['changes'] or 'No changes observed before this refresh',
                         'policy':project.get('git_policy',{}).get('commits','Not agreed')}]
    result={}
    for path,kind,body,title in [('summary.md','summary',summary,'Current situation'),('backlog/product-backlog.md','product_backlog',backlog,'Product backlog')]:
        result[path]=codec.render(kind,project['name']+' — '+title,body,document_path=path,available=available)[0]
    return result
