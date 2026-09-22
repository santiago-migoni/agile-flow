"""Schema 4: clean authored documents and Git-portable technical records."""
import copy
import json
import os
import uuid
from contextlib import contextmanager
try:
    from .release_store import ReleaseStore,engine,Error,hash_text
    from .document_store import DocumentStore,atomic
    from . import clean_markdown as codec
    from .git_workflow import GitWorkflow
except ImportError:
    from release_store import ReleaseStore,engine,Error,hash_text
    from document_store import DocumentStore,atomic
    import clean_markdown as codec
    from git_workflow import GitWorkflow

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
        if manifest!={'schema_version':4,'codec':'clean-markdown-v1'} or engine.digest(baseline)!=meta.get('baseline_integrity'):raise Error('Portable technical records disagree; reconcile the checkout.')
        self.technical=baseline
        return meta

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
        value=copy.deepcopy(data);technical={}
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
        text,schema=codec.render(kind,title,value,old,self.schemas.get(path))
        self.schemas[path]=schema;self.technical[path]=technical
        return text

    def encode(self,state,old):
        desired=super().encode(state,old)
        from pathlib import Path
        for path,kind in [('summary.md','summary'),('backlog/product-backlog.md','product_backlog')]:
            lines=desired[path].split('\n',1)
            template=(Path(__file__).resolve().parents[1]/'templates/markdown'/(kind+'.md')).read_text()
            desired[path]=template.replace('{{title}}',lines[0].lstrip('# ')).replace('{{content}}',lines[1].strip()).rstrip()+'\n'
        return desired

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
        return result

    @contextmanager
    def locked(self):
        self.git.ensure_no_conflicts()
        with super().locked():yield

    def transaction(self,request):
        self.schemas={};self.technical={}
        if request.get('operation')=='initialize' and not self.path.exists():
            if (self.internal/'state.json').exists() or (self.directory/'state.json').exists():raise Error('Migrate existing records before initialization.')
        return super().transaction(request)

    def apply(self,state,request,files):
        if request['operation']=='set-git-policy':
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
        targets['.internal/manifest.json']=json.dumps({'schema_version':4,'codec':'clean-markdown-v1'},indent=2)+'\n'
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
