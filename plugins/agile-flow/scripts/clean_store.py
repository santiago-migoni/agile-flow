"""Schema 4: clean authored documents and Git-portable technical records."""
import copy
import json
import os
import uuid
import posixpath
from contextlib import contextmanager
try:
    from .release_store import ReleaseStore,engine,Error,hash_text
    from .document_store import DocumentStore,atomic
    from . import clean_markdown as codec
    from .git_workflow import GitWorkflow
    from . import design_documents as design
except ImportError:
    from release_store import ReleaseStore,engine,Error,hash_text
    from document_store import DocumentStore,atomic
    import clean_markdown as codec
    from git_workflow import GitWorkflow
    import design_documents as design

TECHNICAL={'document_baseline','planning_baseline','reviewed_fingerprints','fingerprints'}

class CleanStore(ReleaseStore):
    schema_version=4
    metadata_relative='.internal/registry.json'
    pending_relative='.internal/local/pending.json'
    lock_relative='.internal/local/locks/writer.lock'
    backup_relative='.internal/local/backups/registry.json'
    archive_relative='.internal/local/transactions'
    manual_relative='.internal/local/backups/manual'

    def __init__(self,root):
        super().__init__(root)
        self.schemas={};self.technical={};self.git=GitWorkflow(self.root)

    def metadata(self):
        if not self.path.exists() and ((self.internal/'state.json').exists() or (self.directory/'state.json').exists()):
            raise Error('Legacy document schema requires explicit migration.')
        meta=DocumentStore.metadata(self)
        self.schemas=copy.deepcopy(meta.get('document_schemas',{}))
        manifest=json.loads(self.safe('.internal/manifest.json').read_text())
        baseline=json.loads(self.safe('.internal/baselines/records.json').read_text())
        if manifest not in ({'schema_version':4,'codec':'clean-markdown-v1'},{'schema_version':4,'codec':'editorial-v2'}) or engine.digest(baseline)!=meta.get('baseline_integrity'):raise Error('Portable technical records disagree; reconcile the checkout.')
        self.technical=baseline
        return meta

    def decode(self, files, meta):
        # Older layouts retain their original decoder; optional design paths are
        # handled only by the current writer and remain authored authorities.
        core = {path: text for path, text in files.items() if path not in design.DOCUMENTS.values()}
        state = super().decode(core, meta)
        for kind, path in design.DOCUMENTS.items():
            if path in files:
                state[kind] = self.unpack_document(path, files[path])
        self.validate(state)
        return state

    def validate(self,state):
        # Editorial rows add context to previously text-only project lists. The
        # lifecycle engine still receives its original textual validation shape;
        # decisions, permissions and evidence are never synthesized from these rows.
        state.setdefault('product_backlog',[]);state.setdefault('releases',[])
        checked=copy.deepcopy(state)
        for key,primary in [('users','actor'),('confirmed_facts','statement'),('proposals','statement')]:
            values=checked['project'].get(key,[])
            if isinstance(values,list):
                for n,value in enumerate(values):
                    if isinstance(value,dict):
                        if not isinstance(value.get(primary),str) or not value[primary].strip():
                            raise Error('Structured project '+key+' needs '+primary+'.')
                        values[n]=value[primary]
        super().validate(checked)
        for kind in design.DOCUMENTS:
            if state.get(kind) is not None:
                design.validate(kind, state[kind], Error)

    def unpack_document(self,path,text):
        if path not in self.schemas:raise Error('Unknown document schema: '+path)
        value=codec.unpack(text,self.schemas[path])
        def restore(obj,prefix):
            if isinstance(obj,dict):
                for key,val in self.technical.get(path,{}).get(prefix,{}).items():obj[key]=copy.deepcopy(val)
                for key,val in list(obj.items()):
                    if key not in TECHNICAL:restore(val,prefix+'/'+key)
            elif isinstance(obj,list):
                for n,val in enumerate(obj):restore(val,prefix+'/'+('@'+val['id'] if isinstance(val,dict) and isinstance(val.get('id'),str) else str(n)))
        restore(value,'')
        if 'project' in value:
            value['project']['root']=str(self.root)
        return value

    def render_document(self,path,kind,title,data,old):
        display={'project_name':getattr(self,'render_state',{}).get('project',{}).get('name','Not recorded')}
        parts=path.split('/')
        if path.startswith('release/'):
            display['version']=parts[1]
            if len(parts)>=4:
                display['ITER_id']=parts[2]
                increments=[i for i in getattr(self,'render_observed',{}).get('increments',[]) if i['iteration_id']==parts[2]]
                for token,key in [('observed_verification_status','effective_verification'),('current_acceptance_status','effective_acceptance')]:
                    display[token]='; '.join(i['id']+': '+i[key] for i in increments) or 'No delivery recorded'
        value=copy.deepcopy(data);technical={}
        if kind=='planning':
            it=value['iteration'];stories=getattr(self,'render_state',{}).get('backlog',[])
            it['item_documents']=[{'document':f"[{r['id']}](user-stories/{r['id']}.md)",'type':r['type'],
                'contribution':r['purpose'],'estimate':r.get('estimate','Not estimated'),
                'baseline':('Current selected document' if it.get('planning_baseline',{}).get(f"release/{it['release_id']}/{it['id']}/user-stories/{r['id']}.md")==hash_text(self.rendered_documents.get(f"release/{it['release_id']}/{it['id']}/user-stories/{r['id']}.md")) else 'Changed — reconcile plan')} for r in stories if r['id'] in it['item_ids']]
        def remove(obj,prefix):
            if isinstance(obj,dict):
                for key in list(obj):
                    if key in TECHNICAL or (prefix=='/project' and key in {'id','root'}):
                        content=obj.pop(key)
                        if key!='root':technical.setdefault(prefix,{})[key]=content
                    else:remove(obj[key],prefix+'/'+key)
            elif isinstance(obj,list):
                for n,val in enumerate(obj):remove(val,prefix+'/'+('@'+val['id'] if isinstance(val,dict) and isinstance(val.get('id'),str) else str(n)))
        remove(value,'')
        links={}
        for target in getattr(self,'render_paths',set()):
            if target==path:continue
            parts=target.split('/');name=parts[-1]
            identity=None
            if name.startswith(('US-','BL-')):identity=name[:-3]
            elif name=='sprint-planning.md':identity=parts[-2]
            elif name.startswith('release-'):identity=parts[1]
            if identity:links[identity]=posixpath.relpath(target,posixpath.dirname(path) or '.')
        text,schema=codec.render(kind,title,value,old,self.schemas.get(path),document_path=path,available=getattr(self,'render_paths',None),display=display,links=links)
        self.schemas[path]=schema;self.technical[path]=technical
        self.rendered_documents[path]=text
        return text

    def encode(self,state,old):
        self.render_state=state;self.rendered_documents={}
        self.render_observed=engine.inspect_state(self,state)
        self.render_paths=set(old)|{'constitution.md','summary.md','backlog/product-backlog.md'}
        if state.get('roadmap') is not None:self.render_paths.add('roadmap.md')
        self.render_paths.update(path for kind, path in design.DOCUMENTS.items() if state.get(kind) is not None)
        for r in state['product_backlog']:self.render_paths.add(f"backlog/{r['id']}.md")
        for r in state['releases']:self.render_paths.add(f"release/{r['id']}/release-{r['id'][1:]}.md")
        for it in state['iterations']:
            base=f"release/{it['release_id']}/{it['id']}"
            self.render_paths.add(base+'/sprint-planning.md')
            for r in state['backlog']:
                if r['iteration_id']==it['id']:self.render_paths.add(base+'/user-stories/'+r['id']+'.md')
            for name,groups in [('verification',['evidence','blockers']),('review',['reviews']),('retrospective',['improvements'])]:
                path=base+'/'+name+'.md'
                if state.get('report_context',{}).get(path) or any(r['iteration_id']==it['id'] for g in groups for r in state[g]):self.render_paths.add(path)
        desired=super().encode(state,old)
        for kind, path in design.DOCUMENTS.items():
            if state.get(kind) is not None:
                desired[path] = self.render_document(path, kind, state['project']['name']+' — '+kind.replace('_',' ').title(), state[kind], old.get(path))
        try:from .editorial_views import generate
        except ImportError:from editorial_views import generate
        desired.update(generate(self,state,set(desired)))
        return desired

    def render(self,force=False):
        with self.locked():
            meta,files,state=self.read()
            if any(not isinstance(v,dict) or v.get('codec')!='editorial-v2' for v in self.schemas.values()):
                raise Error('Migrate the editorial format explicitly before rendering.')
            if force:
                for path in self.generated:
                    if path in files and hash_text(files[path])!=meta['documents'].get(path):
                        atomic(self.safe(f'{self.manual_relative}/{uuid.uuid4().hex}-{path}'),files[path])
                        meta['documents'][path]=hash_text(files[path])
            schemas=copy.deepcopy(self.schemas);technical=copy.deepcopy(self.technical)
            encoded=self.encode(state,files)
            self.schemas=schemas;self.technical=technical
            desired={**files,**{p:encoded[p] for p in self.generated}}
            return self.commit(meta,files,desired,'render-'+uuid.uuid4().hex,engine.digest(desired))

    def git_preview(self,request):
        self.read()
        preview=self.git.preview(request['paths'])
        prefix=self.directory.relative_to(self.git.repository()).as_posix()+'/'
        changed=self.git.run('status','--porcelain=v1','--untracked-files=all','--',':(top,literal)'+prefix.rstrip('/'))
        selected=set(preview['paths'])
        portable=set(self.inventory())|{self.metadata_relative,'.internal/manifest.json','.internal/baselines/records.json'}
        for path in portable:
            relative=prefix+path
            if relative not in selected and not self.git.run('ls-files','--',':(top,literal)'+relative).strip():
                raise Error('Include all changed Agile Flow records; an untracked portable file is missing: '+relative)
        # Shared registry and documents form one portable snapshot. Do not publish
        # a changed document while leaving its schema/identity metadata behind.
        for line in changed.splitlines():
            path=line[3:]
            if path.startswith(prefix) and '/.internal/local/' not in path and path not in selected:
                raise Error('Include all changed Agile Flow records in the same outcome: '+path)
        return preview

    def git_commit(self,request):
        observed=self.inspect();self.git_preview(request)
        return self.git.commit(request,observed['project'].get('git_policy',{}))

    def fingerprint(self,meta,files):
        return engine.digest({'documents':{p:hash_text(t) for p,t in sorted(files.items())},'registry':meta.get('integrity'),'git':self.git.anchor()})

    def inspect(self):
        result=super().inspect();result['git']=self.git.status()
        for kind, path in design.DOCUMENTS.items():
            if self.safe(path).exists():
                result[kind] = self.unpack_document(path, self.safe(path).read_text())
        return result

    @contextmanager
    def locked(self):
        self.git.ensure_no_conflicts()
        with super().locked():yield

    def transaction(self,request):
        self.schemas={};self.technical={}
        if self.path.exists():
            meta=self.metadata()
            if any(not isinstance(v,dict) or v.get('codec')!='editorial-v2' for v in self.schemas.values()):
                raise Error('Editorial format upgrade requires migrate --dry-run, then migrate --apply with its source fingerprint.')
        if request.get('operation')=='initialize' and not self.path.exists():
            if (self.internal/'state.json').exists() or (self.directory/'state.json').exists():raise Error('Migrate existing records before initialization.')
        return super().transaction(request)

    def apply(self,state,request,files):
        if request['operation'] in {'update-product-design', 'update-architecture'}:
            kind = request['operation'][7:].replace('-', '_')
            design.update(state, kind, request, engine.utc_now(), Error)
        elif request['operation']=='set-git-policy':
            policy=request['policy']
            if policy.get('commits') not in {'on-request','automatic'} or not request.get('source'):raise Error('Git policy needs commit mode and actual user source.')
            if policy.get('commits')=='automatic' and not policy.get('outcomes'):raise Error('Automatic policy must name authorized outcomes.')
            state['project']['git_policy']={**policy,'source':request['source']}
        else:super().apply(state,request,files)

    def commit(self,meta,before,desired,operation_id,request_digest,context=None):
        if self.inventory()!=before:raise Error('Documents changed during transaction.')
        for path in self.generated:
            if path in before and hash_text(before[path])!=meta.get('documents',{}).get(path):raise Error('Generated index was edited; preserve and reconcile it.')
        next_meta=copy.deepcopy(meta)
        next_meta.update(schema_version=4,revision=meta.get('revision',0)+1,documents={p:hash_text(t) for p,t in desired.items()},document_schemas=copy.deepcopy(self.schemas),baseline_integrity=engine.digest(self.technical))
        decoded=self.decode(desired,next_meta)
        next_meta['identities']=sorted(set(meta.get('identities',[]))|{r['id'] for g in self.identity_groups for r in decoded[g]})
        next_meta.setdefault('operations',{})[operation_id]={'digest':request_digest,'revision':next_meta['revision']}
        next_meta.pop('integrity',None);next_meta['integrity']=engine.digest(next_meta)
        targets=dict(desired)
        targets['.internal/manifest.json']=json.dumps({'schema_version':4,'codec':'editorial-v2'},indent=2)+'\n'
        targets['.internal/baselines/records.json']=json.dumps(self.technical,indent=2)+'\n'
        targets[self.metadata_relative]=json.dumps(next_meta,indent=2)+'\n'
        targets['.internal/local/state.json']=json.dumps({'schema_version':4,'revision':next_meta['revision'],'registry_integrity':next_meta['integrity'],'git':self.git.anchor()},indent=2)+'\n'
        # A scoped ignore file travels with the documents and excludes only local data.
        if not (self.directory/'.gitignore').exists():targets['.gitignore']='.internal/local/\n'
        changes={}
        for path in set(before)|set(targets):
            p=self.safe(path);prior=p.read_text() if p.exists() else None;after=targets.get(path)
            if prior!=after:changes[path]={'before':prior,'after':after}
        for path in getattr(self,'migration_retire',[]):
            p=self.safe(path)
            if p.exists() and path not in targets:changes[path]={'before':p.read_text(),'after':None}
        journal={'id':uuid.uuid4().hex,'at':engine.utc_now(),'operation_id':operation_id,'changes':changes,'context':context or {},'git_anchor':self.git.anchor()}
        journal['integrity']=engine.digest(journal)
        atomic(self.safe(self.pending_relative),json.dumps(journal,indent=2))
        self.replay()
        return engine.response('applied',revision=next_meta['revision'],fingerprint=self.fingerprint(next_meta,desired),documents='written',git={'commit':'not-created','reason':'Use git-preview then git-commit for a coherent authorized outcome.'})

    def replay(self):
        journal=json.loads(self.safe(self.pending_relative).read_text())
        if journal.get('git_anchor')!=self.git.anchor():raise Error('Git checkout changed during a pending transaction; preserve the journal and reconcile before recovery.')
        return super().replay()

    def migrate(self,apply=False,request=None):
        try:from .clean_migration import migrate
        except ImportError:from clean_migration import migrate
        return migrate(self,apply,request or {})
