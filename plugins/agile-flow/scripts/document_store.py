"""Schema-2 document authority, recoverable transactions, and legacy migration."""
from __future__ import annotations
import copy
import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path

try:
    from . import legacy_records as engine, markdown_records as md
except ImportError:
    import legacy_records as engine
    import markdown_records as md

Error = engine.RecordError
TYPES = {'story': 'US', 'nfr': 'NFR', 'bug': 'BUG', 'technical': 'TECH', 'research': 'SPIKE', 'unresolved': 'ITEM'}
GENERATED = {'backlog.md', 'summary.md'}


def hash_text(value):
    return hashlib.sha256(value.encode()).hexdigest() if value is not None else None


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.write-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(value); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


class DocumentStore:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.directory = self.root / '.agile-flow'
        self.internal = self.directory / '.internal'
        self.path = self.internal / 'state.json'
        self.pending = self.internal / 'pending.json'

    def safe(self, relative):
        rel = Path(relative)
        if rel.is_absolute() or '..' in rel.parts:
            raise Error('Document paths must stay inside .agile-flow.')
        target = self.directory / rel
        if any(part.is_symlink() for part in [target, *target.parents] if part != self.directory.parent):
            raise Error('Symlinked record paths are not supported.')
        if not target.resolve().is_relative_to(self.directory.resolve()):
            raise Error('Document path escapes the record directory.')
        return target

    @contextmanager
    def locked(self):
        self.safe('.internal/.lock').parent.mkdir(parents=True, exist_ok=True)
        with self.safe('.internal/.lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def metadata(self):
        if self.pending.exists():
            raise Error('Interrupted transaction exists; run recover before reading or writing.')
        if not self.path.exists():
            if (self.directory / 'state.json').exists():
                raise Error('Legacy schema detected. Run migrate --dry-run; migration is explicit.')
            raise Error('No document project exists; initialize first.')
        data = json.loads(self.safe('.internal/state.json').read_text())
        if data.get('schema_version') != 2 or data.get('integrity') != engine.digest({k:v for k,v in data.items() if k != 'integrity'}):
            raise Error('Technical state integrity failed; recover explicitly.')
        return data

    def inventory(self):
        files = {}
        if not self.directory.exists(): return files
        for path in sorted(self.directory.rglob('*.md')):
            relative = path.relative_to(self.directory)
            if relative.parts[0] in {'.internal', 'views'} or 'evidence' in relative.parts:
                continue
            files[str(relative)] = self.safe(str(relative)).read_text()
        return files

    def fingerprint(self, meta, files):
        return engine.digest({'revision': meta['revision'], 'documents': {p: hash_text(t) for p,t in sorted(files.items())}})

    def decode(self, files, meta):
        if 'constitution.md' not in files: raise Error('Constitution is missing.')
        constitution = md.loads(files['constitution.md'])
        state = {'schema_version': 1, 'revision': meta['revision'], 'project': constitution['project'],
                 'decisions': constitution.get('decisions', []), 'history': [], 'quality_policy': [],
                 'backlog': [], 'increments': [], 'evidence': [], 'reviews': [], 'blockers': [], 'improvements': [], 'iterations': [],
                 'roadmap': None, 'definition_of_done': None}
        for name, text in files.items():
            if name in GENERATED or name == 'constitution.md': continue
            if name == 'roadmap.md': state['roadmap'] = md.loads(text)
            elif name == 'definition-of-done.md':
                state['definition_of_done'] = md.loads(text)
                state['quality_policy'] = state['definition_of_done'].get('criteria', [])
            elif name.startswith('backlog/'):
                record = md.loads(text)['item']; record['_path'] = name; state['backlog'].append(record)
            elif name.startswith('iterations/'):
                data = md.loads(text)
                ident = Path(name).parts[1]
                for group in ['evidence','reviews','blockers','improvements']:
                    if any(row.get('iteration_id')!=ident for row in data.get(group,[])): raise Error('Record is stored in the wrong iteration document.')
                if name.endswith('/sprint_planning.md'):
                    iteration = data['iteration']
                    if iteration['id'] != ident: raise Error('Iteration path and ID disagree.')
                    state['iterations'].append(iteration)
                    for inc in data.get('increments', []):
                        if inc.get('iteration_id') != ident: raise Error('Increment belongs to a different iteration.')
                        state['increments'].append(inc)
                elif name.endswith('/verification.md'):
                    state['evidence'].extend(data.get('evidence', [])); state['blockers'].extend(data.get('blockers', []))
                elif name.endswith('/review.md'): state['reviews'].extend(data.get('reviews', []))
                elif name.endswith('/retrospective.md'): state['improvements'].extend(data.get('improvements', []))
                else: raise Error(f'Unknown authoritative iteration document: {name}')
            else: raise Error(f'Unknown document {name}; reference authored external documents instead.')
        for group in ['increments', 'evidence', 'reviews', 'blockers', 'improvements']:
            state[group].sort(key=lambda row: int(row['id'].split('-')[-1]))
        self.validate(state)
        return state

    def validate(self, state):
        engine.Store(self.root).validate(state)
        for key in ['name','purpose','next_step']:
            if not isinstance(state['project'].get(key), str) or not state['project'][key].strip(): raise Error(f'Project {key} must be meaningful text.')
        dod = state.get('definition_of_done')
        if dod is not None and (not isinstance(dod, dict) or not isinstance(dod.get('criteria'), list) or not dod['criteria'] or any(not isinstance(c,str) or not c.strip() for c in dod['criteria'])): raise Error('Definition of Done needs nonempty text criteria.')
        for rule in (dod or {}).get('scoped_criteria',[]):
            if not isinstance(rule,dict) or not isinstance(rule.get('criterion'),str) or not rule['criterion'].strip() or not isinstance(rule.get('types'),list) or not rule['types'] or not set(rule['types']).issubset(set(TYPES)-{'unresolved'}): raise Error('Scoped DoD criteria need a criterion and supported item types.')
        items = {i['id'] for i in state['backlog']}
        for item in state['backlog']:
            if not re.fullmatch(r'(ITEM|US|NFR|BUG|TECH|SPIKE)-[0-9]+',item['id']): raise Error('Invalid typed item ID.')
            if item.get('type') not in TYPES: raise Error('Backlog type must be story, nfr, bug, technical, research, or unresolved.')
            if not item['id'].startswith(TYPES[item['type']] + '-'): raise Error('Backlog type and ID disagree.')
            if item.get('order') is not None and (type(item['order']) is not int or item['order'] < 1): raise Error('Order must be a positive integer.')
            if item['id'] in item.get('dependencies',[]): raise Error('An item cannot depend on itself.')
            if not set(item.get('dependencies', [])).issubset(items): raise Error('Unknown backlog dependency.')
        iteration_ids = [i['id'] for i in state['iterations']]
        if len(iteration_ids) != len(set(iteration_ids)): raise Error('Duplicate iteration ID.')
        for iteration in state['iterations']:
            if not re.fullmatch(r'ITER-\d+', iteration['id']): raise Error('Invalid iteration ID.')
            if iteration.get('state') not in {'draft', 'open', 'paused', 'closed', 'canceled'}: raise Error('Invalid iteration state.')
            if not set(iteration.get('item_ids', [])).issubset(items): raise Error('Iteration refers to unknown work.')
        for inc in state['increments']:
            if inc.get('iteration_id') not in iteration_ids: raise Error('Increment has no iteration.')
            iteration = engine.find(state['iterations'], inc['iteration_id'], 'iteration')
            if engine.active_development(inc, state['project']) and iteration['state'] != 'open': raise Error('Active development requires an open iteration.')
        for group in ['evidence', 'reviews', 'blockers', 'improvements']:
            for row in state[group]:
                if row.get('iteration_id') not in iteration_ids: raise Error(f'{group} record needs an iteration.')
                if group != 'improvements' and engine.find(state['increments'],row['increment_id'],'increment')['iteration_id'] != row['iteration_id']: raise Error('Record and increment iterations disagree.')
        if state.get('roadmap'):
            mvp=state['roadmap'].get('mvp',{})
            if isinstance(mvp,dict) and not set(mvp.get('item_ids',[])).issubset(items): raise Error('MVP refers to unknown work.')
            for milestone in state['roadmap'].get('milestones', []):
                if not set(milestone.get('item_ids', [])).issubset(items): raise Error('Roadmap refers to unknown work.')

    def read(self):
        meta = self.metadata(); files = self.inventory()
        missing=set(meta['documents'])-set(files)-GENERATED
        if missing: raise Error('Authored documents are missing; restore them before continuing: '+', '.join(sorted(missing)))
        state=self.decode(files,meta)
        current_ids={row['id'] for group in ['backlog','iterations','increments','decisions','evidence','reviews','blockers','improvements'] for row in state[group]}
        historical_aliases={old for old,new in meta.get('legacy_item_mapping',{}).items() if old!=new and new in current_ids}
        removed=set(meta.get('identities',[]))-current_ids-historical_aliases
        if removed: raise Error('Recorded identities were removed; preserve history and use explicit retirement: '+', '.join(sorted(removed)))
        return meta, files, state

    def inspect(self):
        meta, files, state = self.read()
        result = engine.inspect_state(self, state)
        result.update(schema_version=2, fingerprint=self.fingerprint(meta, files), iterations=state['iterations'],
                      roadmap=state['roadmap'], definition_of_done=state['definition_of_done'])
        hashes = {p:hash_text(t) for p,t in files.items()}
        result['document_changes'] = [p for p in sorted(set(hashes)|set(meta['documents'])) if hashes.get(p) != meta['documents'].get(p)]
        result['documents'] = sorted(files)
        ranks = [i.get('order') for i in state['backlog'] if i.get('order') is not None]
        result['ordering_warning'] = 'Duplicate or missing order; display ties by ID. Refine explicitly.' if len(ranks) != len(state['backlog']) or len(ranks) != len(set(ranks)) else None
        return result

    def encode(self, state, old):
        desired = {}
        def add(path, title, data):
            desired[path] = md.patch(old[path], data) if path in old else md.dumps(title, data)
            if md.loads(desired[path])!=data: raise Error('Document serialization would change content: '+path)
        add('constitution.md', 'Project constitution', {'project': state['project'], 'decisions': state['decisions']})
        for name, key, title in [('roadmap.md','roadmap','Product roadmap'), ('definition-of-done.md','definition_of_done','Definition of Done')]:
            if state.get(key) is not None: add(name, title, state[key])
        for item in state['backlog']:
            data = {k:v for k,v in item.items() if k != '_path'}
            name = item.get('_path', f"backlog/{item['id']}.md")
            previous=next((p for p,t in old.items() if p.startswith('backlog/') and md.loads(t).get('item',{}).get('id')==item.get('legacy_id')),None)
            if name not in old and previous:
                desired[name]=md.patch(old[previous],{'item':data})
            else: add(name, item['id'] + ' — ' + item['purpose'], {'item': data})
        for iteration in state['iterations']:
            ident = iteration['id']; base = f'iterations/{ident}/'
            deliveries=[i for i in state['increments'] if i['iteration_id']==ident]
            add(base+'sprint_planning.md', ident+' — Sprint planning', {'iteration': iteration, 'increments': deliveries})
            if base+'sprint_planning.md' not in old and not deliveries:
                desired[base+'sprint_planning.md']=desired[base+'sprint_planning.md'].replace('\n\n','\n\nPlanning alone does not authorize execution. Delivery authorization, when present, is recorded under Increments.\n\n',1)
            for file, groups in [('verification.md',['evidence','blockers']), ('review.md',['reviews']), ('retrospective.md',['improvements'])]:
                data = {group:[x for x in state[group] if x['iteration_id']==ident] for group in groups}
                if any(data.values()) or base+file in old: add(base+file, ident+' — '+file[:-3].capitalize(), data)
        observed = engine.inspect_state(self, state)
        def cell(value): return str(value).replace('|','\\|').replace('\n',' ')
        backlog = ['# Product backlog', '', 'Generated index. Edit the item documents; changes here require reconciliation.', '', '| Order | ID | Type | Need | Estimate | State | Iterations |', '| --- | --- | --- | --- | --- | --- | --- |']
        current_items=[i for i in state['backlog'] if i['state']!='retired']
        for item in sorted(current_items, key=lambda x:(x.get('order') or float('inf'), x['id'])):
            assignments = ', '.join(i['id'] for i in state['iterations'] if item['id'] in i.get('item_ids', [])) or 'Unassigned'
            path = item.get('_path', f"backlog/{item['id']}.md")
            backlog.append(f"| {item.get('order', 'Unranked')} | [{item['id']}]({path}) | {item['type']} | {cell(item['purpose'])} | {cell(item.get('estimate', 'Not estimated'))} | {item['state']} | {assignments} |")
        retired=[i for i in state['backlog'] if i['state']=='retired']
        if retired:
            backlog+=['','## Retired work','']+[f"- [{i['id']}]({i.get('_path', 'backlog/'+i['id']+'.md')}): {i.get('retirement_reason','See item history.')}" for i in retired]
        desired['backlog.md'] = '\n'.join(backlog)+'\n'
        lines = ['# Current situation', '', 'Generated summary; authored documents remain authoritative.', '', state['project']['purpose'], '', f"Next step: {state['project']['next_step']}", '', '[Constitution](constitution.md) · [Backlog](backlog.md)', '', '## Iterations']
        for it in state['iterations']: lines.append(f"- [{it['id']}](iterations/{it['id']}/sprint_planning.md): {it['goal']} ({it['state']}).")
        for inc in observed['increments']: lines.append(f"- {inc['id']}: development {inc['states']['development']}; verification {inc['effective_verification']}; acceptance {inc['effective_acceptance']}.")
        lines += ['', '## Open questions'] + [f'- {q}' for q in state['project'].get('open_questions', [])]
        lines += ['', '## Blockers'] + [f"- {b['id']}: {b['condition']}" for b in state['blockers'] if b['state']=='open']
        desired['summary.md'] = '\n'.join(lines)+'\n'
        return desired

    def commit(self, meta, before, desired, operation_id, request_digest, context=None):
        """Write-ahead journal with before/after bytes; replay refuses unrelated edits."""
        current = self.inventory()
        if current != before: raise Error('Documents changed during the transaction; retry from inspect.')
        for path in GENERATED:
            if path in before and hash_text(before[path]) != meta.get('documents', {}).get(path):
                raise Error(f'Generated index was edited: {path}. Preserve and reconcile before render --force.')
        next_meta = copy.deepcopy(meta)
        next_meta.update(schema_version=2, revision=meta.get('revision',0)+1, documents={p:hash_text(t) for p,t in desired.items()})
        decoded=self.decode(desired,next_meta)
        next_meta['identities']=sorted(set(meta.get('identities',[])) | {row['id'] for group in ['backlog','iterations','increments','decisions','evidence','reviews','blockers','improvements'] for row in decoded[group]})
        next_meta.setdefault('operations', {})[operation_id] = {'digest': request_digest, 'revision': next_meta['revision']}
        next_meta.pop('integrity',None); next_meta['integrity'] = engine.digest(next_meta)
        changes = {p:{'before':before.get(p),'after':desired.get(p)} for p in set(before)|set(desired) if before.get(p)!=desired.get(p)}
        old_metadata = self.path.read_text() if self.path.exists() else None
        changes['.internal/state.json'] = {'before':old_metadata,'after':json.dumps(next_meta,indent=2)+'\n'}
        if old_metadata is not None:
            backup=self.safe('.internal/state.backup.json')
            atomic(backup, old_metadata)
        journal={'id':uuid.uuid4().hex, 'at':engine.utc_now(), 'operation_id':operation_id, 'changes':changes, 'source_documents':before, 'context':context or {}}
        journal['integrity']=engine.digest(journal)
        atomic(self.safe('.internal/pending.json'),json.dumps(journal,indent=2))
        self.replay()
        return engine.response('applied', revision=next_meta['revision'], fingerprint=self.fingerprint(next_meta,desired), documents='written')

    def replay(self):
        journal=json.loads(self.safe('.internal/pending.json').read_text())
        if journal.get('integrity') != engine.digest({k:v for k,v in journal.items() if k!='integrity'}): raise Error('Transaction journal integrity failed.')
        for path, change in journal['changes'].items():
            p=self.safe(path); current=p.read_text() if p.exists() else None
            if current not in (change['before'], change['after']): raise Error(f'Recovery conflict in {path}; preserve user changes before recovery.')
        # Metadata is committed last. Read commands refuse a pending journal.
        for path, change in sorted(journal['changes'].items(), key=lambda x:x[0]=='.internal/state.json'):
            p=self.safe(path)
            if change['after'] is None:
                if p.exists(): p.unlink()
            else: atomic(p,change['after'])
        archive=self.safe(f".internal/transactions/{journal['id']}.json")
        archive.parent.mkdir(parents=True,exist_ok=True)
        os.replace(self.pending,archive)

    def recover(self):
        with self.locked():
            if not self.pending.exists(): raise Error('No interrupted document transaction exists. Backups are preserved under .internal/transactions/.')
            self.replay()
        return engine.response('applied', recovery='completed')

    def transaction(self, request):
        if not request.get('operation_id') or not request.get('purpose'): raise Error('Operation ID and purpose are required.')
        with self.locked():
            if self.pending.exists(): raise Error('Recover the interrupted transaction first.')
            digest=engine.digest({k:v for k,v in request.items() if k not in {'expected_revision','expected_fingerprint'}})
            if request['operation']=='initialize' and not self.path.exists():
                if (self.directory/'state.json').exists(): raise Error('Migrate legacy records explicitly before initialization.')
                if self.inventory(): raise Error('Existing documents must be adopted, not overwritten by initialization.')
                state=engine.initial_state(self.root,request)
                state.update(iterations=[],roadmap=None,definition_of_done={'criteria':state['quality_policy']} if state.get('quality_policy') else None)
                state['project'].pop('preparation',None)
                state['project']={k:v for k,v in state['project'].items() if v not in ([], {})}
                for key in ['background','vision','mission','objectives','agreements','scope','exclusions','stakeholders','success_factors']:
                    if key in request.get('project',{}): state['project'][key]=request['project'][key]
                meta={'schema_version':2,'revision':0,'documents':{},'operations':{}}; files={}
            else:
                meta,files,state=self.read()
                existing=meta['operations'].get(request['operation_id'])
                if existing:
                    if existing['digest']!=digest: raise Error('Operation ID reused with different content.')
                    return engine.response('already_applied',revision=existing['revision'])
                if request.get('expected_revision')!=meta['revision'] or request.get('expected_fingerprint')!=self.fingerprint(meta,files):
                    return engine.response('conflict',errors=['Stale revision or document fingerprint.'])
                missing=set(meta['documents'])-set(files)-GENERATED
                if missing: raise Error('Authored documents were removed; restore them and retire records explicitly: '+', '.join(sorted(missing)))
                self.apply(state,request,files)
                if request['operation']=='classify-backlog':
                    old=request['item_id'];new=next(i['id'] for i in state['backlog'] if i.get('legacy_id')==old)
                    meta.setdefault('legacy_item_mapping',{})[old]=new
            self.validate(state)
            return self.commit(meta,files,self.encode(state,files),request['operation_id'],digest,{'operation':request['operation'],'purpose':request['purpose'],'provenance':request.get('provenance',{})})

    def apply(self,state,request,files):
        op=request['operation']
        if op=='update-project':
            values=request.get('project',{})
            allowed={'name','purpose','constraints','references','next_step','assumptions','open_questions','success_criteria','root','users','confirmed_facts','proposals','background','vision','mission','objectives','agreements','scope','exclusions','stakeholders','success_factors'}
            if not values or set(values)-allowed: raise Error('Unsupported project fields. Use plan-iteration instead of preparation.')
            if 'root' in values and values['root']!=str(self.root): raise Error('Project root must match the selected checkout.')
            state['project'].update(values)
            state['project'].setdefault('amendments',[]).append({'at':engine.utc_now(),'reason':request['purpose'],'source':request.get('provenance',{})})
        elif op in {'update-roadmap','update-dod'}:
            data=request.get('document')
            if not isinstance(data,dict) or not data: raise Error('Provide meaningful document content.')
            if op=='update-dod' and not data.get('criteria'): raise Error('Definition of Done requires criteria.')
            state['roadmap' if op=='update-roadmap' else 'definition_of_done']=data
        elif op=='update-backlog':
            data=request['item']; old_ids={i['id'] for i in state['backlog']}
            kind=data.get('type')
            if not data.get('id') and kind not in TYPES: raise Error('New items require an explicit supported type.')
            engine.mutate(state,request,self.root)
            item=engine.find(state['backlog'],data['id'],'item') if data.get('id') else next(i for i in state['backlog'] if i['id'] not in old_ids)
            if not data.get('id'):
                prefix=TYPES[kind]; nums=[int(i['id'].split('-')[-1]) for i in state['backlog'] if i is not item and i['id'].startswith(prefix+'-')]
                item['id']=f'{prefix}-{max(nums,default=0)+1:03d}'
            for key in ['order','estimate','estimate_basis','story','value','scope','exclusions','reproduction','expected','observed','question','work_limit','findings','quality_attribute','verification_method','impact','recommendation','applicability']:
                if key in data: item[key]=data[key]
        elif op=='classify-backlog':
            item=engine.find(state['backlog'],request['item_id'],'item')
            kind=request.get('type')
            if item['type']!='unresolved' or kind not in TYPES or kind=='unresolved' or not request.get('reason'): raise Error('Classification needs an unresolved item, supported type and reason.')
            old=item['id'];prefix=TYPES[kind]
            number=max([int(i['id'].split('-')[-1]) for i in state['backlog'] if i['id'].startswith(prefix+'-')],default=0)+1
            new=f'{prefix}-{number:03d}'
            item.update(id=new,type=kind,legacy_id=old,classification_reason=request['reason'],_path=f'backlog/{new}.md')
            def remap(ids): return [new if value==old else value for value in ids]
            for row in state['backlog']: row['dependencies']=remap(row.get('dependencies',[]))
            for row in state['iterations']+state['increments']: row['item_ids']=remap(row.get('item_ids',[]))
            for decision in state['decisions']:
                if isinstance(decision.get('scope'),dict) and 'item_ids' in decision['scope']: decision['scope']['item_ids']=remap(decision['scope']['item_ids'])
            for milestone in (state.get('roadmap') or {}).get('milestones',[]): milestone['item_ids']=remap(milestone.get('item_ids',[]))
        elif op=='retire-backlog':
            if not request.get('reason'): raise Error('Retirement needs a reason.')
            item=engine.find(state['backlog'],request['item_id'],'item'); item.update(state='retired',retirement_reason=request['reason'])
        elif op=='reorder-backlog':
            ids=request['item_ids']
            if len(ids)!=len(set(ids)) or set(ids)!={i['id'] for i in state['backlog']}: raise Error('Reorder must contain every item exactly once.')
            for index,ident in enumerate(ids,1): engine.find(state['backlog'],ident,'item')['order']=index
        elif op=='plan-iteration':
            data=request['iteration']
            if not data.get('goal') or not data.get('scope') or not data.get('item_ids'): raise Error('Iteration needs goal, scope, and selected items.')
            if 'id' in data:
                iteration=engine.find(state['iterations'],data['id'],'iteration')
                if any(i['iteration_id']==iteration['id'] for i in state['increments']): raise Error('Delivery planning is baselined; create another iteration or use correction operations.')
            else:
                number=max([int(i['id'].split('-')[-1]) for i in state['iterations']],default=0)+1
                iteration={'id':f'ITER-{number:03d}','state':'draft','changes':[]};state['iterations'].append(iteration)
            forbidden={'authorization','states','state','increments','baseline'}
            if forbidden & set(data): raise Error('Planning does not set execution or acceptance state.')
            iteration.update(data)
            iteration['item_documents']=['['+i['id']+' criteria](../../'+i.get('_path','backlog/'+i['id']+'.md')+'#criteria)' for i in state['backlog'] if i['id'] in iteration['item_ids']]
            iteration['planning_baseline']={name:hash_text(text) for name,text in files.items() if name=='definition-of-done.md' or any(name==i.get('_path') for i in state['backlog'] if i['id'] in iteration['item_ids'])}
            iteration.setdefault('changes',[]).append({'at':engine.utc_now(),'reason':request['purpose']})
        elif op=='prepare':
            iteration=engine.find(state['iterations'],request['iteration_id'],'iteration')
            if iteration['state'] not in {'draft','open'}: raise Error('Iteration is not available for execution preparation.')
            if any(i['type']=='unresolved' for i in state['backlog'] if i['id'] in request['increment'].get('item_ids',[])): raise Error('Classify unresolved work before execution preparation.')
            if not state['definition_of_done']: raise Error('Define applicable quality criteria before authorized preparation.')
            if iteration.get('open_decisions'): raise Error('Resolve material product decisions before execution preparation.')
            if not request['increment'].get('item_ids'): raise Error('Select backlog work before preparing a delivery.')
            if not set(request['increment'].get('item_ids',[])).issubset(iteration['item_ids']): raise Error('Increment exceeds selected iteration items.')
            for path,expected in iteration.get('planning_baseline',{}).items():
                if hash_text(files.get(path))!=expected: raise Error('Selected planning baseline changed; revise the draft iteration before preparing delivery.')
            data=copy.deepcopy(request)
            checks=data['increment'].get('required_checks',[])
            selected_types={i['type'] for i in state['backlog'] if i['id'] in data['increment']['item_ids']}
            scoped=[rule['criterion'] for rule in state['definition_of_done'].get('scoped_criteria',[]) if selected_types.intersection(rule['types'])]
            data['increment']['required_checks']=list(dict.fromkeys(checks+state['definition_of_done']['criteria']+scoped))
            engine.mutate(state,data,self.root)
            inc=state['increments'][-1];inc['iteration_id']=iteration['id']
            inc['document_baseline']={name:hash_text(text) for name,text in files.items() if name=='definition-of-done.md' or any(name==i.get('_path') for i in state['backlog'] if i['id'] in inc['item_ids'])}
            # Baseline source contents remain in transaction snapshots; the plan keeps references only.
            iteration['state']='open'
        elif op in {'pause','close','reopen'} and request.get('target')=='iteration':
            iteration=engine.find(state['iterations'],request['iteration_id'],'iteration')
            if not request.get('reason') or request.get('action',op) not in {op,'cancel'}: raise Error('Iteration transition requires a reason and valid action.')
            for inc in state['increments']:
                if inc['iteration_id']==iteration['id']:
                    engine.mutate(state,{**request,'target':'increment','increment_id':inc['id']},self.root)
            iteration.setdefault('changes',[]).append({'at':engine.utc_now(),'reason':request.get('reason',request['purpose']),'operation':op})
            iteration['state']={'pause':'paused','close':'closed','reopen':'open'}[op] if request.get('action')!='cancel' else 'canceled'
        elif op=='record-improvement':
            iteration=engine.find(state['iterations'],request['iteration_id'],'iteration')
            engine.mutate(state,request,self.root);state['improvements'][-1]['iteration_id']=iteration['id']
        else:
            before={group:len(state[group]) for group in ['evidence','reviews','blockers']}
            engine.mutate(state,request,self.root)
            for group,count in before.items():
                for record in state[group][count:]:
                    inc=engine.find(state['increments'],record['increment_id'],'increment');record['iteration_id']=inc['iteration_id']
            if request.get('increment_id'):
                inc=engine.find(state['increments'],request['increment_id'],'increment')
                if op in {'start','resume'}:
                    iteration=engine.find(state['iterations'],inc['iteration_id'],'iteration')
                    if iteration['state'] not in {'open','paused'}: raise Error('Reopen the iteration before starting work.')
                    iteration['state']='open'

    def render(self,force=False):
        with self.locked():
            meta,files,state=self.read()
            if force:
                for path in GENERATED:
                    if path in files and hash_text(files[path])!=meta['documents'].get(path):
                        backup=self.safe(f'.internal/manual/{uuid.uuid4().hex}-{path}');atomic(backup,files[path])
                        meta['documents'][path]=hash_text(files[path])
            desired=dict(files); generated=self.encode(state,files)
            for path in GENERATED: desired[path]=generated[path]
            return self.commit(meta,files,desired,'render-'+uuid.uuid4().hex,engine.digest(desired))

    def migrate(self,apply=False,request=None):
        request=request or {}
        if self.pending.exists(): raise Error('Interrupted migration or transaction exists; run recover first.')
        if self.path.exists():
            self.read()
            return engine.response('already_applied',schema_version=2)
        legacy=engine.Store(self.root)
        state=legacy.read()
        source_hash=engine.file_hash(legacy.path)
        files_to_preserve={str(p.relative_to(self.directory)):engine.file_hash(p) for p in self.directory.rglob('*') if p.is_file() and '.internal' not in p.parts}
        preview_fingerprint=engine.digest(files_to_preserve)
        manual_views=[]
        if legacy.view_manifest.exists():
            try:
                manifest=json.loads(legacy.view_manifest.read_text()).get('files',{})
                manual_views=[name for name,expected in manifest.items() if files_to_preserve.get('views/'+name)!=expected]
            except (ValueError,AttributeError): manual_views=['View manifest is unreadable; all views preserved for review.']
        mapping={}; unresolved=[]
        if manual_views: unresolved.append('Legacy views contain manual changes; review preserved originals before adopting their meaning.')
        types=request.get('item_types',{})
        counters={}
        for item in state['backlog']:
            old=item['id']; kind=types.get(old, item['type'] if item.get('type') in TYPES else 'unresolved')
            if kind not in TYPES: raise Error('Invalid explicit migration type.')
            if kind=='unresolved': new=old;unresolved.append(f'{old}: classify before development.')
            else:
                prefix=TYPES[kind];counters[prefix]=counters.get(prefix,0)+1;new=f'{prefix}-{counters[prefix]:03d}'
            mapping[old]=new;item.update(id=new,type=kind,legacy_id=old)
        # Replace only typed item-reference locations, never source quotations or historical prose.
        for item in state['backlog']: item['dependencies']=[mapping.get(i,i) for i in item.get('dependencies',[])]
        for decision in state['decisions']:
            if isinstance(decision.get('scope'),dict) and 'item_ids' in decision['scope']:
                decision['scope']['item_ids']=[mapping[i] for i in decision['scope']['item_ids']]
        for inc in state['increments']: inc['item_ids']=[mapping[i] for i in inc['item_ids']]
        state.update(iterations=[],roadmap=None,definition_of_done={'criteria':state['quality_policy']} if state.get('quality_policy') else None)
        for number,inc in enumerate(state['increments'],1):
            ident=f'ITER-{number:03d}';inc['iteration_id']=ident
            state['iterations'].append({'id':ident,'goal':inc['objective'],'scope':inc['scope'],'item_ids':inc['item_ids'],'state':inc.get('administrative_state','open'), 'legacy_increment_id':inc['id'], 'baseline_limitation':'Legacy item and DoD baselines may be unavailable; original records preserved in the migration backup.'})
        for group in ['evidence','reviews','blockers']:
            for row in state[group]: row['iteration_id']=engine.find(state['increments'],row['increment_id'],'legacy increment')['iteration_id']
        for review in state['reviews']:
            if 'evidence_ids' not in review:
                ids=engine.legacy_review_evidence_ids(state,review)
                if ids is not None: review['evidence_ids']=ids
        preparation=state['project'].pop('preparation',{})
        if preparation:
            ident=f"ITER-{len(state['iterations'])+1:03d}"
            state['iterations'].append({**preparation,'id':ident,'state':'draft','goal':preparation.get('objective','Legacy proposal'), 'scope':preparation.get('scope','Needs refinement'), 'item_ids':[mapping[i] for i in preparation.get('item_ids',[])]})
        if state['improvements']:
            if not state['iterations']:
                state['iterations'].append({'id':'ITER-001','state':'draft','goal':'Legacy learning context','scope':'Historical improvements; no execution authorized.','item_ids':[]})
                unresolved.append('Project-level learning placed in a draft historical context; review attribution.')
            for row in state['improvements']:
                row['iteration_id']=state['iterations'][-1]['id'];row['migration_note']='Legacy project-level improvement; iteration attribution unverified.'
        unresolved += ['Roadmap and MVP require authored planning.']
        if not state['definition_of_done']: unresolved.append('Definition of Done is not recorded.')
        self.validate(state)
        desired=self.encode(state,{})
        conflicts=sorted(set(self.inventory()) | {p for p in desired if self.safe(p).exists()})
        report=engine.response('preview',source_fingerprint=preview_fingerprint,manual_view_edits=manual_views,item_mapping=mapping,documents=sorted(desired),preserved_files=files_to_preserve,unresolved=unresolved,conflicts=conflicts)
        if not apply: return report
        if request.get('expected_source_fingerprint')!=preview_fingerprint: raise Error('Migration requires the current dry-run source fingerprint.')
        if conflicts: raise Error('Migration targets already exist; preserve and resolve them first.')
        with self.locked():
            if self.path.exists(): return engine.response('already_applied',schema_version=2)
            with legacy.lock_path.open('a+') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                if engine.file_hash(legacy.path)!=source_hash: raise Error('Legacy state changed after preview.')
                backup=self.safe('.internal/legacy-backup')
                if backup.exists():
                    for saved in backup.rglob('*'):
                        if saved.is_file() and engine.file_hash(saved)!=files_to_preserve.get(str(saved.relative_to(backup))): raise Error('Previous migration backup conflicts with the source; preserve and resolve it.')
                backup.mkdir(exist_ok=True)
                for relative,expected in files_to_preserve.items():
                    path=self.safe(relative)
                    if engine.file_hash(path)!=expected: raise Error('Legacy input changed during migration.')
                    target=backup/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
                    if engine.file_hash(target)!=expected: raise Error('Legacy backup verification failed.')
                meta={'schema_version':2,'revision':state['revision'],'documents':{},'operations':{},'legacy_item_mapping':mapping,'migration_source_fingerprint':preview_fingerprint}
                result=self.commit(meta,{},desired,'migrate-'+preview_fingerprint,engine.digest(request))
                result.update(unresolved=unresolved,backup=str(backup),legacy_records='preserved as inactive history; new CLI uses authored documents')
                return result
