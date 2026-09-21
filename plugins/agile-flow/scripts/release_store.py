"""Schema 3: product needs, release-owned iterations, and typed US work records."""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path
try:
    from .document_store import DocumentStore, Error, engine, hash_text, atomic
    from . import template_documents as docs
except ImportError:
    from document_store import DocumentStore, Error, engine, hash_text, atomic
    import template_documents as docs

KINDS = {'US','NFR','BUG','TCH','SPK','unresolved'}
VERSION = r'v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?'


def conditions(values, prefix):
    if not isinstance(values,list): raise Error('Criteria and DoD must be lists.')
    result=[]
    for n,value in enumerate(values,1):
        if isinstance(value,str):
            value={'id':f'{prefix}-{n:02d}', 'result' if prefix=='AC' else 'requirement':value}
        if not isinstance(value,dict):raise Error('Conditions must be text or structured rows.')
        row=copy.deepcopy(value)
        if not re.fullmatch(prefix+r'-[0-9]{2,}',row.get('id','')):raise Error('Condition needs a stable '+prefix+' ID.')
        content=row.get('result') if prefix=='AC' else row.get('requirement')
        if not isinstance(content,str) or not content.strip():raise Error('Condition needs a meaningful expected result or requirement.')
        result.append(row)
    if len({r['id'] for r in result})!=len(result):raise Error('Duplicate condition IDs.')
    return result


def next_id(rows, prefix, width=4):
    return f"{prefix}-{max([int(r['id'].split('-')[-1]) for r in rows],default=0)+1:0{width}d}"


def iteration_path(it):
    return f"release/{it['release_id']}/{it['id']}"


def story_path(story, state):
    it=engine.find(state['iterations'],story['iteration_id'],'iteration')
    return iteration_path(it)+f"/user-stories/{story['id']}.md"


def clean(record):
    return {k:v for k,v in record.items() if not k.startswith('_')}


def cell(value):
    return str(value).replace('|','&#124;').replace('\n',' ')


class ReleaseStore(DocumentStore):
    schema_version = 3
    generated = {'backlog/product-backlog.md','summary.md'}
    identity_groups = DocumentStore.identity_groups + ['product_backlog','releases']

    def transaction(self, request):
        if request.get('operation') == 'initialize' and request.get('quality_policy'):
            raise Error('Define DoD on each story; initialization does not accept a global quality policy.')
        return super().transaction(request)

    def metadata(self):
        if self.path.exists() and not self.pending.exists():
            version=json.loads(self.path.read_text()).get('schema_version')
            if version != 3: raise Error('Older document schema detected; run migrate --dry-run explicitly.')
        return super().metadata()

    def decode(self, files, meta):
        if 'constitution.md' not in files: raise Error('Constitution is missing.')
        definition=docs.unpack(files['constitution.md'])
        state={'schema_version':1,'revision':meta['revision'],'project':definition['project'],
               'decisions':definition.get('decisions',[]),'history':[],'quality_policy':[],
               'roadmap':None,'definition_of_done':None}
        for key in self.identity_groups:
            if key!='decisions':state[key]=[]
        for path,text in files.items():
            if path in self.generated or path=='constitution.md':continue
            value=docs.unpack(text)
            if path=='roadmap.md':state['roadmap']=value
            elif re.fullmatch(r'backlog/BL-[0-9]{4,}\.md',path):
                row=value['item'];row['_path']=path
                if path!=f"backlog/{row['id']}.md":raise Error('Product item path and identity disagree.')
                state['product_backlog'].append(row)
            elif path.startswith('release/'):
                parts=Path(path).parts;version=parts[1]
                if len(parts)==3 and parts[2]==f'release-{version[1:]}.md':
                    row=value['release']
                    if row['id']!=version:raise Error('Release path and identity disagree.')
                    state['releases'].append(row)
                elif len(parts)>=4:
                    ident=parts[2]
                    if len(parts)==5 and parts[3]=='user-stories':
                        row=value['item'];row['_path']=path
                        if parts[4]!=row['id']+'.md' or row['iteration_id']!=ident or row['release_id']!=version:raise Error('Story path and assignment disagree.')
                        state['backlog'].append(row)
                    elif len(parts)==4 and parts[3]=='sprint-planning.md':
                        row=value['iteration']
                        if row['id']!=ident or row['release_id']!=version:raise Error('Iteration path and assignment disagree.')
                        state['iterations'].append(row)
                        for inc in value.get('increments',[]):
                            if inc['iteration_id']!=ident:raise Error('Increment belongs to another iteration.')
                            state['increments'].append(inc)
                    elif len(parts)==4 and parts[3] in {'verification.md','review.md','retrospective.md'}:
                        groups={'verification.md':['evidence','blockers'],'review.md':['reviews'],'retrospective.md':['improvements']}[parts[3]]
                        for group in groups:
                            for row in value.get(group,[]):
                                if row['iteration_id']!=ident:raise Error('Report record belongs to another iteration.')
                                state[group].append(row)
                        # Authored report context is retained alongside the managed event lists.
                        state.setdefault('report_context',{})[path]={k:v for k,v in value.items() if k not in groups}
                    else:raise Error('Unknown release document: '+path)
                else:raise Error('Unknown release document: '+path)
            else:raise Error('Unknown document: '+path)
        for path in state.get('report_context', {}):
            parts=Path(path).parts
            it=engine.find(state['iterations'],parts[2],'iteration')
            if it['release_id']!=parts[1]:raise Error('Report path and iteration release disagree.')
        for group in self.identity_groups:
            state[group].sort(key=lambda r:r['id'])
        self.validate(state)
        return state

    def validate(self,state):
        state.setdefault('product_backlog',[]);state.setdefault('releases',[])
        engine.Store(self.root).validate(state)
        for key in ['name','purpose','next_step']:
            if not isinstance(state['project'].get(key),str) or not state['project'][key].strip():raise Error('Project '+key+' needs meaningful text.')
        all_ids=[row['id'] for group in self.identity_groups for row in state[group]]
        if len(all_ids)!=len(set(all_ids)):raise Error('Duplicate record identity.')
        products={row['id'] for row in state['product_backlog']}
        releases={row['id'] for row in state['releases']}
        iterations={row['id'] for row in state['iterations']}
        stories={row['id'] for row in state['backlog']}
        for product in state['product_backlog']:
            if not re.fullmatch(r'BL-[0-9]{4,}',product['id']) or not product.get('purpose'):raise Error('Product need requires BL identity and purpose.')
            if product.get('target_release') and product['target_release'] not in releases:raise Error('Unknown target release.')
            if not set(product.get('dependencies',[])).issubset(products):raise Error('Unknown product dependency.')
        for release in state['releases']:
            if not re.fullmatch(VERSION,release['id']) or not release.get('objective'):raise Error('Release needs a valid version and objective.')
            if not set(release.get('item_ids',[])).issubset(products):raise Error('Release scope must reference BL records.')
            if release.get('status') not in {'draft','planned','released','canceled'}:raise Error('Invalid release status.')
        for it in state['iterations']:
            if not re.fullmatch(r'ITER-[0-9]{3,}',it['id']) or it.get('release_id') not in releases:raise Error('Iteration needs identity and a known release.')
            if it.get('state') not in {'draft','open','paused','closed','canceled'}:raise Error('Invalid iteration state.')
            if not set(it.get('item_ids',[])).issubset(stories):raise Error('Iteration refers to unknown stories.')
            for ident in it.get('item_ids',[]):
                if engine.find(state['backlog'],ident,'story')['iteration_id']!=it['id']:raise Error('Selected story belongs to another iteration.')
        for item in state['backlog']:
            if not re.fullmatch(r'US-[0-9]{4,}',item['id']) or item.get('type') not in KINDS:raise Error('Stories use US-nnnn identities and US/NFR/BUG/TCH/SPK types.')
            if item.get('parent_id') not in products or item.get('iteration_id') not in iterations:raise Error('Story needs a BL parent and iteration.')
            it=engine.find(state['iterations'],item['iteration_id'],'iteration')
            if item.get('release_id')!=it['release_id']:raise Error('Story release disagrees with its iteration.')
            for key in ['criteria','dod']:
                values=item.get(key,[])
                conditions(values,'AC' if key=='criteria' else 'DOD')
            if not set(item.get('dependencies',[])).issubset(stories):raise Error('Unknown story dependency.')
        for group in ['product_backlog','backlog']:
            for row in state[group]:
                if row.get('order') is not None and (type(row['order'])!=int or row['order']<1):raise Error('Order must be a positive integer.')
        for inc in state['increments']:
            if inc.get('iteration_id') not in iterations:raise Error('Increment has no iteration.')
            it=engine.find(state['iterations'],inc['iteration_id'],'iteration')
            if not set(inc['item_ids']).issubset(it['item_ids']):raise Error('Delivery exceeds selected iteration work.')
            if engine.active_development(inc,state['project']) and it['state']!='open':raise Error('Active work requires an open iteration.')
        for group in ['evidence','reviews','blockers','improvements']:
            for row in state[group]:
                if row.get('iteration_id') not in iterations:raise Error('Report record needs an iteration.')
                if group!='improvements' and engine.find(state['increments'],row['increment_id'],'increment')['iteration_id']!=row['iteration_id']:raise Error('Record and delivery iterations disagree.')
        if state.get('roadmap'):
            if 'mvp' in state['roadmap']:raise Error('Detailed MVP definition belongs in the release.')
            for entry in state['roadmap'].get('versions',[]):
                if not re.fullmatch(VERSION,entry.get('version','')):raise Error('Roadmap stages need version identifiers.')

    def inspect(self):
        meta,files,state=self.read()
        observed=engine.inspect_state(self,state)
        observed.update(schema_version=3,fingerprint=self.fingerprint(meta,files),stories=observed.pop('backlog'),
                        backlog=state['product_backlog'],releases=state['releases'],iterations=state['iterations'],roadmap=state['roadmap'],documents=sorted(files))
        observed['document_changes']=[p for p in sorted(set(files)|set(meta['documents'])) if hash_text(files.get(p))!=meta['documents'].get(p)]
        return observed

    def encode(self,state,old):
        desired={}
        def add(path,kind,title,data):
            desired[path]=docs.render(kind,title,data,old.get(path))
        add('constitution.md','constitution',state['project']['name']+' — Project constitution',{'project':state['project'],'decisions':state['decisions']})
        if state.get('roadmap') is not None:add('roadmap.md','roadmap','Product roadmap',state['roadmap'])
        for item in state['product_backlog']:
            data=clean(item)
            data['story_links']=[{'story':s['id'],'document':f"[{s['id']}](../{story_path(s,state)})",'type':s['type'],'release':s['release_id'],'iteration':s['iteration_id']} for s in state['backlog'] if s['parent_id']==item['id']]
            add(f"backlog/{item['id']}.md",'product_item',item['id']+' — '+item['purpose'],{'item':data})
        for release in state['releases']:
            data=clean(release)
            data['iteration_links']=[{'iteration':it['id'],'document':f"[{it['id']}]({it['id']}/sprint-planning.md)",'goal':it['goal']} for it in state['iterations'] if it['release_id']==release['id']]
            add(f"release/{release['id']}/release-{release['id'][1:]}.md",'release',release['id']+' — '+release['objective'],{'release':data})
        # Capture each newly selected story before rendering the plan. Refinement
        # retains this baseline until plan-iteration explicitly refreshes it.
        for story in state['backlog']:
            path=story_path(story,state)
            add(path,'story',story['id']+' — '+story['purpose'],{'item':clean(story)})
            it=engine.find(state['iterations'],story['iteration_id'],'iteration')
            it.setdefault('planning_baseline',{}).setdefault(path,hash_text(desired[path]))
        for it in state['iterations']:
            base=iteration_path(it);data=clean(it)
            data['item_documents']=[f"[{s['id']}](user-stories/{s['id']}.md) — acceptance criteria and Definition of Done" for s in state['backlog'] if s['id'] in it['item_ids']]
            data['authorization_note']='Planning does not authorize execution. See sourced authorization references on each prepared delivery.'
            add(base+'/sprint-planning.md','planning',it['id']+' — '+it['goal'],{'iteration':data,'increments':[i for i in state['increments'] if i['iteration_id']==it['id']]})
            for filename,kind,groups in [('verification.md','verification',['evidence','blockers']),('review.md','review',['reviews']),('retrospective.md','retrospective',['improvements'])]:
                path=base+'/'+filename
                records={key:[r for r in state[key] if r['iteration_id']==it['id']] for key in groups}
                records.update(state.get('report_context',{}).get(path,{}))
                if any(records.values()) or path in old:add(path,kind,it['id']+' — '+kind.capitalize(),records)
        lines=['# Product backlog','','Generated index. Product needs own their details; stories own their acceptance criteria and DoD.','','| Order | Item | Expected value | Status | Target release |','| --- | --- | --- | --- | --- |']
        for item in sorted(state['product_backlog'],key=lambda r:(r.get('order') or float('inf'),r['id'])):
            lines.append(f"| {item.get('order','Unranked')} | [{item['id']} — {cell(item['purpose'])}]({item['id']}.md) | {cell(item.get('value','Not recorded'))} | {item['state']} | {item.get('target_release') or 'Unassigned'} |")
        desired['backlog/product-backlog.md']='\n'.join(lines)+'\n'
        observed=engine.inspect_state(self,state)
        summary=['# '+state['project']['name']+' — Current situation','','## Product objective','',state['project']['purpose'],'','## Current releases and iterations','']
        for release in state['releases']:summary.append(f"- [{release['id']}](release/{release['id']}/release-{release['id'][1:]}.md): {release['objective']} ({release['status']}).")
        for it in state['iterations']:summary.append(f"- [{it['id']}]({iteration_path(it)}/sprint-planning.md): {it['goal']} ({it['state']}).")
        summary+=['','## Delivery status','','| Delivery | Development | Verification | User acceptance |','| --- | --- | --- | --- |']
        for inc in observed['increments']:summary.append(f"| {inc['id']} | {inc['states']['development']} | {inc['effective_verification']} | {inc['effective_acceptance']} |")
        summary+=['','## Blockers and pending decisions','']+[f"- {b['condition']}" for b in state['blockers'] if b['state']=='open']+[f'- {q}' for q in state['project'].get('open_questions',[])]
        summary+=['','## Next useful action','',state['project']['next_step'],'','[Constitution](constitution.md) · [Product backlog](backlog/product-backlog.md)']
        desired['summary.md']='\n'.join(summary)+'\n'
        return desired

    def apply(self,state,request,files):
        op=request['operation']
        if op in {'update-dod','classify-backlog'}:raise Error('Use update-story: type and DoD belong to each US record.')
        if op=='update-roadmap':
            state['roadmap']=request['document']
        elif op=='update-report':
            it=engine.find(state['iterations'],request['iteration_id'],'iteration')
            kind=request['document']
            allowed={'verification':{'scope','conclusion'},'review':{'presented_result','resulting_work','unresolved_feedback'},'retrospective':{'retain','follow_up'}}
            fields=request.get('fields',{})
            if kind not in allowed or not fields or set(fields)-allowed[kind]:
                raise Error('Report context cannot replace managed evidence, acceptance or improvement records.')
            path=iteration_path(it)+'/'+kind+'.md'
            state.setdefault('report_context',{}).setdefault(path,{}).update(fields)
        elif op=='update-backlog':
            data=request['item']
            if not data.get('purpose'):raise Error('Product need requires purpose.')
            if any(r['purpose'].casefold()==data['purpose'].casefold() and r['id']!=data.get('id') for r in state['product_backlog']):raise Error('Potential duplicate product need; refine the existing record.')
            if data.get('id'):row=engine.find(state['product_backlog'],data['id'],'product need')
            else:
                row={'id':next_id(state['product_backlog'],'BL'),'state':'open','changes':[]};state['product_backlog'].append(row)
            allowed={'id','purpose','value','users','outcome','scope','exclusions','success_indicators','dependencies','assumptions','open_questions','order','priority','provenance','references','target_release'}
            if set(data)-allowed:raise Error('Unsupported BL fields; detailed criteria and DoD belong to stories.')
            row.update(data);row.setdefault('changes',[]).append({'at':engine.utc_now(),'reason':request['purpose']})
        elif op in {'retire-backlog','complete-backlog'}:
            if not request.get('reason'):raise Error('A sourced reason is required.')
            row=engine.find(state['product_backlog'],request['item_id'],'product need')
            row.update(state='retired' if op=='retire-backlog' else 'completed',change_reason=request['reason'])
        elif op=='reorder-backlog':
            ids=request['item_ids']
            if len(ids)!=len(set(ids)) or set(ids)!={r['id'] for r in state['product_backlog']}:raise Error('Reorder every BL exactly once.')
            for n,ident in enumerate(ids,1):engine.find(state['product_backlog'],ident,'product need')['order']=n
        elif op=='update-release':
            data=request['release'];ident=data.get('id')
            if not re.fullmatch(VERSION,ident or ''):raise Error('Release ID must be a version such as v0.1.0.')
            row=next((r for r in state['releases'] if r['id']==ident),None)
            if row is None:row={'id':ident,'status':'draft','changes':[]};state['releases'].append(row)
            if row['status']=='released':raise Error('Published release is historical; create a later release rather than rewriting it.')
            row.update(data);row.setdefault('changes',[]).append({'at':engine.utc_now(),'reason':request['purpose']})
            if row.get('status')=='released' and (not row.get('publication') or not row.get('delivered_outcome')):raise Error('Released status needs actual delivered outcome and publication references.')
        elif op=='plan-iteration':
            data=request['iteration']
            if not data.get('goal') or not data.get('scope'):raise Error('Iteration needs a meaningful goal and scope.')
            forbidden={'state','authorization','increments','baseline','planning_baseline'}
            if set(data)&forbidden:raise Error('Draft planning does not grant execution or alter a baseline directly.')
            if data.get('id'):
                row=engine.find(state['iterations'],data['id'],'iteration')
                if any(i['iteration_id']==row['id'] for i in state['increments']):raise Error('Plan is baselined; use correction operations or another iteration.')
                if data.get('release_id',row['release_id'])!=row['release_id']:raise Error('Iteration identity cannot move between releases implicitly.')
            else:
                engine.find(state['releases'],data.get('release_id'),'release')
                row={'id':next_id(state['iterations'],'ITER',3),'state':'draft','item_ids':[],'changes':[]};state['iterations'].append(row)
            row.update(data)
            row['planning_baseline']={p:hash_text(t) for p,t in files.items() if any(s['id'] in row['item_ids'] and p==story_path(s,state) for s in state['backlog'])}
            row.setdefault('changes',[]).append({'at':engine.utc_now(),'reason':request['purpose']})
        elif op=='update-story':
            data=request['story']
            if not data.get('purpose'):raise Error('Story needs purpose.')
            if data.get('id'):
                row=engine.find(state['backlog'],data['id'],'story')
                for key in ['parent_id','iteration_id','release_id']:
                    if data.get(key,row[key])!=row[key]:raise Error('Story identity and assignment are stable; create linked follow-up work for another iteration.')
            else:
                it=engine.find(state['iterations'],data.get('iteration_id'),'iteration')
                if any(i['iteration_id']==it['id'] for i in state['increments']):raise Error('Cannot silently extend a baselined iteration.')
                row={'id':next_id(state['backlog'],'US'),'state':'open','release_id':it['release_id'],'criteria':[],'dod':[],'changes':[]};state['backlog'].append(row)
                it['item_ids'].append(row['id'])
            if set(data)&{'states','authorization','baseline','document_baseline'}:raise Error('Story updates do not grant execution or acceptance.')
            row.update(data)
            for key,prefix in [('criteria','AC'),('dod','DOD')]:row[key]=conditions(row.get(key,[]),prefix)
            row.setdefault('changes',[]).append({'at':engine.utc_now(),'reason':request['purpose']})
        elif op=='prepare':
            it=engine.find(state['iterations'],request['iteration_id'],'iteration')
            if it['state'] not in {'draft','open'} or it.get('open_decisions'):raise Error('Resolve iteration state and material decisions before preparation.')
            data=copy.deepcopy(request);payload=data['increment'];ids=payload.get('item_ids',[])
            if not ids or not set(ids).issubset(it['item_ids']):raise Error('Select stories from this iteration.')
            selected=[engine.find(state['backlog'],i,'story') for i in ids]
            if any(s['type']=='unresolved' or not s['criteria'] or not s['dod'] or s.get('open_questions') for s in selected):raise Error('Selected stories need resolved type, criteria, DoD and material questions.')
            for path,expected in it.get('planning_baseline',{}).items():
                if hash_text(files.get(path))!=expected:raise Error('Planning baseline changed; refine the draft plan before preparation.')
            # Freeze criteria and item-local quality requirements, never use a global DoD.
            payload['criteria']=[s['id']+'/'+v['id']+': '+v['result'] for s in selected for v in conditions(s['criteria'],'AC')]
            payload['required_checks']=list(dict.fromkeys(payload.get('required_checks',[])+[s['id']+'/'+v['id']+': '+v['requirement'] for s in selected for v in conditions(s['dod'],'DOD')]))
            engine.mutate(state,data,self.root)
            inc=state['increments'][-1];inc['iteration_id']=it['id']
            inc['document_baseline']={story_path(s,state):hash_text(files[story_path(s,state)]) for s in selected}
            inc['story_baseline']={s['id']:{'criteria':copy.deepcopy(s['criteria']),'dod':copy.deepcopy(s['dod'])} for s in selected}
            it['state']='open'
        else:
            super().apply(state,request,files)

    def migrate(self,apply=False,request=None):
        try:
            from .release_migration import migrate
        except ImportError:
            from release_migration import migrate
        return migrate(self,apply,request or {})
