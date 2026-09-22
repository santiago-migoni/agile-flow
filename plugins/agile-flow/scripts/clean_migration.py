"""Read-only migration previews and recoverable conversion of prior document schemas."""
import copy
import json
import shutil
import tempfile
try:
    from .release_store import ReleaseStore,Error,engine,hash_text
    from . import clean_markdown as codec
except ImportError:
    from release_store import ReleaseStore,Error,engine,hash_text
    import clean_markdown as codec


def inventory(store):
    values={}
    for p in sorted(store.directory.rglob('*')):
        rel=p.relative_to(store.directory).as_posix()
        if rel.startswith('.internal/local/') or rel.startswith('.internal/migration-backups/'):continue
        if p.is_symlink():raise Error('Migration does not follow symlinks.')
        if p.is_file():values[rel]=engine.file_hash(store.safe(rel))
    return values


def migrate(store,apply,request):
    if store.pending.exists() or (store.internal/'pending.json').exists():raise Error('Recover the pending transaction before migration.')
    if store.path.exists():
        store.read()
        if all(isinstance(v,dict) and v.get('codec')=='editorial-v2' for v in store.schemas.values()):
            return engine.response('already_applied',schema_version=4,codec='editorial-v2')
    hashes=inventory(store)
    if not hashes:raise Error('No project records to migrate.')
    fingerprint=engine.digest(hashes)
    source_schema=4 if store.path.exists() else 1
    if source_schema!=4 and (store.internal/'state.json').exists():
        source_schema=json.loads((store.internal/'state.json').read_text()).get('schema_version')
    with tempfile.TemporaryDirectory(prefix='af-clean-migration-') as temp:
        from pathlib import Path
        root=Path(temp);shutil.copytree(store.directory,root/'.agile-flow')
        if source_schema==4:
            old=type(store)(root)
        else:old=ReleaseStore(root)
        unresolved=[]
        if source_schema not in {3,4}:
            preview=old.migrate(request=request)
            if preview.get('blocking'):return engine.response('preview',source_fingerprint=fingerprint,source_schema=source_schema,target_schema=4,blocking=preview['blocking'])
            result=old.migrate(True,{**request,'expected_source_fingerprint':preview['source_fingerprint']});unresolved=result.get('unresolved',[])
        meta,marked,state=old.read()
        state['project']['root']=str(store.root)
        originals={}
        for path,text in marked.items():
            if path in store.generated:originals[path]=text;continue
            if source_schema==4:
                store.schemas[path]=copy.deepcopy(old.schemas[path]);store.technical[path]=copy.deepcopy(old.technical.get(path,{}));originals[path]=text
            else:
                plain,schema=codec.strip(text);store.schemas[path]=schema;originals[path]=plain
        desired=store.encode(state,originals)
        # Preserve a valid draft baseline across a format-only conversion. A baseline
        # already changed in the source remains stale and requires actual replanning.
        for it in state['iterations']:
            for path,prior in it.get('planning_baseline',{}).items():
                if path in marked and prior==hash_text(marked[path]):it['planning_baseline'][path]=hash_text(desired[path])
        desired=store.encode(state,desired)
        store.validate(store.decode(desired,meta))
    source=store.inventory()
    report=engine.response('preview',source_schema=source_schema,target_schema=4,target_codec='editorial-v2',source_fingerprint=fingerprint,documents=sorted(desired),blocking=[],unresolved=unresolved,changes={p:{'before':source.get(p),'after':desired.get(p)} for p in set(source)|set(desired) if source.get(p)!=desired.get(p)},preserved_files=hashes)
    if not apply:return report
    if request.get('expected_source_fingerprint')!=fingerprint:raise Error('Migration needs the reviewed source fingerprint.')
    with store.locked():
        if inventory(store)!=hashes:raise Error('Migration source changed since preview.')
        backup='.internal/local/backups/migration-'+fingerprint[:16]
        for rel,expected in hashes.items():
            target=store.safe(backup+'/'+rel);target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and engine.file_hash(target)!=expected:raise Error('Migration backup conflicts with its source.')
            if not target.exists():shutil.copy2(store.safe(rel),target)
            if engine.file_hash(target)!=expected:raise Error('Migration backup verification failed.')
        # Old metadata remains an inert legacy source until the new registry commits.
        # It is then retired by the same recoverable journal, not left as a second authority.
        base={'revision':meta['revision'],'documents':{p:hash_text(t) for p,t in source.items()},'operations':meta.get('operations',{}),'identities':meta.get('identities',[])}
        store.migration_retire=[rel for rel in hashes if rel.startswith('.internal/') or rel in {'state.json','state.backup.json'} or rel.startswith('views/')]
        result=store.commit(base,source,desired,'clean-migration-'+fingerprint,engine.digest(request),{'operation':'migrate','backup':backup})
        result.update(backup=backup,unresolved=unresolved);return result
