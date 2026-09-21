"""Previewable schema-1/2 migration with explicit release attribution."""
from __future__ import annotations
import copy
import json
import re
import shutil
import tempfile
from pathlib import Path
try:
    from .document_store import DocumentStore, engine, Error, hash_text
    from .release_store import VERSION, next_id, conditions
except ImportError:
    from document_store import DocumentStore, engine, Error, hash_text
    from release_store import VERSION, next_id, conditions


def inventory(store):
    result={}
    if not store.directory.exists():raise Error('No legacy project exists.')
    for p in sorted(store.directory.rglob('*')):
        rel=str(p.relative_to(store.directory))
        if rel.startswith('.internal/migration-backups/'):continue
        if p.is_symlink():raise Error('Migration does not follow symlinks.')
        if p.is_file():result[rel]=engine.file_hash(store.safe(rel))
    return result


def source_state(store):
    if store.path.exists():
        version=json.loads(store.path.read_text()).get('schema_version')
        if version==3:
            store.read();return None,None,3
        meta,_,state=DocumentStore(store.root).read()
        return state,meta,2
    with tempfile.TemporaryDirectory(prefix='af-migration-preview-') as tmp:
        root=Path(tmp);shutil.copytree(store.directory,root/'.agile-flow')
        previous=DocumentStore(root);preview=previous.migrate()
        if preview['conflicts']:raise Error('Resolve legacy target conflicts: '+str(preview['conflicts']))
        previous.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        meta,_,state=previous.read()
        return copy.deepcopy(state),meta,1


def transform(source,request):
    state=copy.deepcopy(source);old_items=state['backlog']
    state.update(backlog=[],product_backlog=[],releases=[])
    products={};stories={};unresolved=[];blocking=[]
    for old in old_items:
        ident=next_id(state['product_backlog'],'BL');products[old['id']]=ident
        state['product_backlog'].append({'id':ident,'purpose':old['purpose'],'state':old.get('state','open'),
            'value':old.get('value','Not established by legacy records.'),'order':old.get('order'),
            'priority':old.get('priority',{}),'provenance':old.get('provenance',{}),
            'legacy_details':{k:v for k,v in old.items() if not k.startswith('_')},'changes':[]})
    for it in state['iterations']:
        version=request.get('iteration_releases',{}).get(it['id'])
        if not version or not re.fullmatch(VERSION,version):
            blocking.append('Assign an explicit release version to '+it['id']);continue
        definition=request.get('releases',{}).get(version,{})
        if not definition.get('objective'):
            blocking.append('Supply a sourced or proposed release objective for '+version);continue
        it['release_id']=version
        if not any(r['id']==version for r in state['releases']):state['releases'].append({**definition,'id':version,'status':'draft'})
        mapping={}
        for old_id in it.get('item_ids',[]):
            old=engine.find(old_items,old_id,'legacy item');ident=next_id(state['backlog'],'US');mapping[old_id]=ident
            kind=request.get('item_types',{}).get(old_id,{'story':'US','nfr':'NFR','bug':'BUG','technical':'TCH','research':'SPK'}.get(old.get('type'),'unresolved'))
            quality=source.get('definition_of_done') or {};dod=list(quality.get('criteria',[]))
            dod += [r['criterion'] for r in quality.get('scoped_criteria',[]) if old.get('type') in r['types']]
            item={k:v for k,v in old.items() if not k.startswith('_')}
            item.update(id=ident,type=kind,parent_id=products[old_id],iteration_id=it['id'],release_id=version,
                        criteria=conditions(old.get('criteria',[]),'AC'),dod=conditions(dod,'DOD'),legacy_id=old_id)
            state['backlog'].append(item);stories.setdefault(old_id,[]).append(ident)
            if kind=='unresolved' or not item['criteria'] or not dod:unresolved.append(ident+': refine type, criteria or DoD before new execution.')
        for story in state['backlog']:
            if story['iteration_id']!=it['id']:continue
            story['legacy_dependencies']=story.pop('dependencies',[])
            story['dependencies']=[mapping[d] for d in story['legacy_dependencies'] if d in mapping]
            if any(d not in mapping for d in story['legacy_dependencies']):unresolved.append(story['id']+': review preserved cross-iteration dependency references.')
        for inc in state['increments']:
            if inc['iteration_id']==it['id']:inc['item_ids']=[mapping[i] for i in inc['item_ids']]
        it['item_ids']=list(mapping.values())
        for key in ['planning_baseline','item_documents']:
            if key in it:it['legacy_'+key]=it.pop(key)
        it['migration_note']='Legacy delivery baselines preserved; review draft scope before new execution.'
    if blocking:return state,products,stories,unresolved,blocking
    for decision in state['decisions']:
        scope=decision.get('scope')
        if isinstance(scope,dict) and 'item_ids' in scope:
            decision['legacy_scope']=copy.deepcopy(scope)
            scope['item_ids']=[sid for old in scope['item_ids'] for sid in stories.get(old,[])]
            if not scope['item_ids'] and decision.get('kind')=='authorization':unresolved.append(decision['id']+': legacy permission has no assigned stories; rebind actual scope before execution.')
    roadmap=state.get('roadmap')
    if roadmap and 'mvp' in roadmap:
        target=request.get('mvp_release')
        if target not in {r['id'] for r in state['releases']}:blocking.append('Choose mvp_release from mapped releases to preserve the legacy MVP.')
        else:engine.find(state['releases'],target,'release')['mvp']=roadmap.pop('mvp')
    if roadmap:
        for milestone in roadmap.get('milestones',[]):
            if 'item_ids' in milestone:milestone['item_ids']=[products.get(i,i) for i in milestone['item_ids']]
        if not roadmap.get('versions'):unresolved.append('Refine preserved roadmap context into version stages; no versions inferred.')
    if source.get('definition_of_done') and not state['backlog']:unresolved.append('Legacy quality policy is preserved in backup; select item DoD when stories are created.')
    state['definition_of_done']=None;state['quality_policy']=[]
    for release in state['releases']:release['item_ids']=list(dict.fromkeys(s['parent_id'] for s in state['backlog'] if s['release_id']==release['id']))
    return state,products,stories,unresolved,blocking


def migrate(store,apply,request):
    if store.pending.exists():raise Error('Recover the pending transaction before migration.')
    hashes=inventory(store);fingerprint=engine.digest(hashes)
    source,meta,schema=source_state(store)
    if source is None:return engine.response('already_applied',schema_version=3)
    state,products,stories,unresolved,blocking=transform(source,request)
    before=store.inventory();desired={}
    if not blocking:store.validate(state);desired=store.encode(state,{})
    backup_name=f'.internal/migration-backups/schema-{schema}-'+fingerprint[:16]
    report=engine.response('preview',source_schema=schema,target_schema=3,source_fingerprint=fingerprint,
        product_mapping=products,story_mapping=stories,documents=sorted(desired),preserved_files=hashes,
        backup=backup_name,unresolved=unresolved,blocking=blocking,
        manual_edits=[p for p,t in before.items() if p in meta.get('documents',{}) and hash_text(t)!=meta['documents'][p]])
    if not apply:return report
    if blocking:raise Error('Resolve migration mapping: '+'; '.join(blocking))
    if request.get('expected_source_fingerprint')!=fingerprint:raise Error('Migration needs current dry-run source fingerprint.')
    with store.locked():
        if store.pending.exists():raise Error('Recover before migration.')
        current=inventory(store)
        if '.internal/.lock' not in hashes:current.pop('.internal/.lock',None)
        if current!=hashes:raise Error('Legacy records changed after preview.')
        backup=store.safe(backup_name);backup.mkdir(parents=True,exist_ok=True)
        for rel,expected in hashes.items():
            src=store.safe(rel);target=store.safe(backup_name+'/'+rel)
            if target.exists() and engine.file_hash(target)!=expected:raise Error('Previous migration backup conflicts with source.')
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():shutil.copy2(src,target)
            if engine.file_hash(target)!=expected:raise Error('Migration backup verification failed.')
        state['project'].setdefault('migration_notes',[]).append('Original schema '+str(schema)+' documents and manual prose preserved in '+backup_name+'. Review originals before reconciling notes.')
        desired=store.encode(state,{})
        metadata={'schema_version':3,'revision':source['revision'],'documents':{p:hash_text(t) for p,t in before.items()},
                  'operations':{},'legacy_product_mapping':products,'legacy_story_mapping':stories,'migration_source_fingerprint':fingerprint}
        result=store.commit(metadata,before,desired,'migration-'+fingerprint,engine.digest(request),{'operation':'migrate','source_schema':schema,'backup':backup_name})
        result.update(backup=backup_name,unresolved=unresolved,product_mapping=products,story_mapping=stories)
        return result
