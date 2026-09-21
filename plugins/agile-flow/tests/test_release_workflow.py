"""Current-layout tests. All projects and failure injection are isolated."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from scripts.release_store import ReleaseStore, Error, engine, story_path
from scripts.document_store import DocumentStore
from scripts import document_store, template_documents as docs

class ReleaseWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.store=ReleaseStore(self.root);self.seq=0
    def op(self,operation,**kw):
        self.seq+=1;r={'operation':operation,'operation_id':str(self.seq),'purpose':'Test actual requested scope',**kw}
        if self.store.path.exists():
            o=self.store.inspect();r.update(expected_revision=o['revision'],expected_fingerprint=o['fingerprint'])
        result=self.store.transaction(r);self.assertEqual(result['status'],'applied',result);return result
    def setup_plan(self):
        self.op('initialize',project={'name':'Bookly','purpose':'Book without messages','vision':'Independent scheduling'})
        self.op('update-backlog',item={'purpose':'Book independently','value':'Less coordination'})
        self.op('update-release',release={'id':'v0.1.0','objective':'Booking MVP','item_ids':['BL-0001'],'mvp':{'hypothesis':'Customers book independently','feedback':'Observe pilot'}})
        self.op('plan-iteration',iteration={'release_id':'v0.1.0','goal':'First booking','scope':'Prepared calendar'})
        self.op('update-story',story={'parent_id':'BL-0001','iteration_id':'ITER-001','type':'US','purpose':'Select a slot','criteria':['One booking persists'],'dod':['Check persistence']})
    def authorize(self):
        self.op('record-decision',decision={'kind':'authorization','author':'user','reason':'Implement selected story','scope':{'item_ids':['US-0001']},'source':'Test user message','quote':'Implement this story.'})
    def prepare(self):
        self.setup_plan();self.authorize()
        self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Prepared calendar','authorization':'DEC-0001'})
    def test_tree_and_functional_authority(self):
        self.setup_plan();o=self.store.inspect();paths=set(o['documents'])
        self.assertIn('backlog/BL-0001.md',paths);self.assertIn('backlog/product-backlog.md',paths)
        self.assertIn('release/v0.1.0/ITER-001/user-stories/US-0001.md',paths)
        self.assertNotIn('definition-of-done.md',paths);self.assertNotIn('backlog.md',paths)
        self.assertEqual(o['schema_version'],3);self.assertEqual(o['increments'],[])
        self.assertEqual(o['stories'][0]['parent_id'],'BL-0001')
        self.assertNotIn('Book without messages',self.store.path.read_text())
    def test_all_five_types_share_us_identity(self):
        self.setup_plan()
        for kind in ['NFR','BUG','TCH','SPK']:
            self.op('update-story',story={'parent_id':'BL-0001','iteration_id':'ITER-001','type':kind,'purpose':kind+' need','criteria':['Observable result'],'dod':['Evidence']})
        stories=self.store.inspect()['stories']
        self.assertEqual([s['id'] for s in stories],[f'US-{i:04d}' for i in range(1,6)])
        self.assertEqual({s['type'] for s in stories},{'US','NFR','BUG','TCH','SPK'})
    def test_mvp_owned_by_release(self):
        self.setup_plan()
        with self.assertRaisesRegex(Error,'MVP'):self.op('update-roadmap',document={'mvp':{'scope':'Wrong location'}})
        self.op('update-roadmap',document={'direction':'Learn first','versions':[{'version':'v0.1.0','stage':'First booking'}]})
        self.assertEqual(self.store.inspect()['releases'][0]['mvp']['hypothesis'],'Customers book independently')
    def test_story_dod_is_required_and_frozen(self):
        self.setup_plan();self.authorize()
        self.op('update-story',story={'id':'US-0001','purpose':'Select a slot','dod':[]})
        with self.assertRaisesRegex(Error,'DoD'):self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        self.op('update-story',story={'id':'US-0001','purpose':'Select a slot','dod':['Check persistence']})
        self.op('plan-iteration',iteration={'id':'ITER-001','goal':'First booking','scope':'Prepared calendar'})
        self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        prior=copy.deepcopy(self.store.inspect()['increments'][0])
        self.op('update-story',story={'id':'US-0001','purpose':'Select a slot','dod':['Stricter later requirement']})
        current=self.store.inspect()['increments'][0]
        self.assertEqual(current['required_checks'],prior['required_checks']);self.assertEqual(current['story_baseline'],prior['story_baseline'])
    def test_no_authorization_from_plan(self):
        self.setup_plan()
        with self.assertRaises(Error):self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-unknown'})
        self.assertEqual(self.store.inspect()['decisions'],[])
    def test_evidence_acceptance_and_stale_product(self):
        self.prepare();self.op('start',increment_id='INC-0001');(self.root/'app.py').write_text('v1')
        self.op('mark-implemented',increment_id='INC-0001')
        check=self.store.inspect()['increments'][0]['required_checks'][0]
        self.op('record-evidence',evidence={'increment_id':'INC-0001','check':check,'result':'passed','scope':'Booking','paths':['app.py']})
        self.op('record-review',review={'increment_id':'INC-0001','decision':'accepted','user_quote':'I accept this result.'})
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'accepted')
        self.op('record-evidence',evidence={'increment_id':'INC-0001','check':check,'result':'passed','scope':'Booking','paths':['app.py']})
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'accepted')
        (self.root/'app.py').write_text('v2')
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'pending')
        paths=self.store.inspect()['documents'];self.assertIn('release/v0.1.0/ITER-001/review.md',paths)
    def test_authored_edits_and_notes_survive(self):
        self.setup_plan();p=self.store.directory/'constitution.md'
        p.write_text(p.read_text().replace('Independent scheduling','Self-service scheduling')+'\nOwner note stays.\n')
        self.op('update-project',project={'next_step':'Review the release'})
        self.assertIn('Owner note stays.',p.read_text());self.assertEqual(self.store.inspect()['project']['vision'],'Self-service scheduling')
    def test_generated_manual_edits_preserved(self):
        self.setup_plan();p=self.store.directory/'backlog/product-backlog.md';p.write_text('Manual ranking request')
        with self.assertRaisesRegex(Error,'Generated index'):self.op('update-project',project={'next_step':'Review'})
        self.store.render(force=True)
        self.assertTrue(any(p.read_text()=='Manual ranking request' for p in (self.store.internal/'manual').rglob('*.md')))
    def test_interrupted_write_recovery(self):
        self.setup_plan();original=document_store.atomic
        def fail(path,value):
            if path.name=='constitution.md':raise OSError('Interrupted')
            return original(path,value)
        with patch.object(document_store,'atomic',side_effect=fail):
            with self.assertRaises(OSError):self.op('update-project',project={'purpose':'Recovered change'})
        with self.assertRaises(Error):self.store.inspect()
        self.store.recover();self.assertEqual(self.store.inspect()['project']['purpose'],'Recovered change')
    def test_published_release_requires_evidence_and_is_not_rewritten(self):
        self.setup_plan()
        with self.assertRaisesRegex(Error,'publication'):self.op('update-release',release={'id':'v0.1.0','status':'released'})
        self.op('update-release',release={'id':'v0.1.0','status':'released','delivered_outcome':'Synthetic release fixture','publication':{'tag':'v0.1.0','source':'Synthetic test fixture'}})
        with self.assertRaisesRegex(Error,'historical'):self.op('update-release',release={'id':'v0.1.0','objective':'Replace published scope'})
    def legacy_fixture(self,with_iteration=True):
        old=DocumentStore(self.root);counter=0
        def mutate(operation,**kw):
            nonlocal counter
            counter+=1;r={'operation':operation,'operation_id':'old-'+str(counter),'purpose':'Legacy fixture',**kw}
            if old.path.exists():
                seen=old.inspect();r.update(expected_revision=seen['revision'],expected_fingerprint=seen['fingerprint'])
            result=old.transaction(r);self.assertEqual(result['status'],'applied')
        mutate('initialize',project={'name':'Legacy','purpose':'Book appointments'})
        mutate('update-backlog',item={'type':'story','purpose':'Book a slot','criteria':['Booking exists']})
        mutate('update-dod',document={'criteria':['unit']})
        if with_iteration:mutate('plan-iteration',iteration={'goal':'Book','scope':'One calendar','item_ids':['US-001']})
        return old,mutate
    def test_schema2_migration_mapping_backup_and_idempotence(self):
        old,_=self.legacy_fixture();p=old.directory/'constitution.md';p.write_text(p.read_text()+'\nManual legacy note\n')
        before={str(p.relative_to(old.directory)):p.read_bytes() for p in old.directory.rglob('*') if p.is_file()}
        preview=self.store.migrate();self.assertTrue(preview['blocking'])
        mapping={'iteration_releases':{'ITER-001':'v0.1.0'},'releases':{'v0.1.0':{'objective':'Booking MVP'}}}
        preview=self.store.migrate(request=mapping);self.assertFalse(preview['blocking'])
        self.assertEqual(before,{str(p.relative_to(old.directory)):p.read_bytes() for p in old.directory.rglob('*') if p.is_file()})
        result=self.store.migrate(True,{**mapping,'expected_source_fingerprint':preview['source_fingerprint']})
        for path,data in before.items():self.assertEqual((self.store.directory/result['backup']/path).read_bytes(),data)
        self.assertEqual(self.store.inspect()['stories'][0]['dod'][0]['requirement'],'unit')
        self.assertEqual(self.store.migrate()['status'],'already_applied')
    def test_unassigned_legacy_need_does_not_invent_release_or_story(self):
        self.legacy_fixture(False);preview=self.store.migrate();self.assertEqual(preview['blocking'],[])
        self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        seen=self.store.inspect();self.assertEqual(len(seen['backlog']),1);self.assertEqual(seen['stories'],[]);self.assertEqual(seen['releases'],[])
    def test_migrated_acceptance_is_preserved(self):
        old,mutate=self.legacy_fixture()
        mutate('record-decision',decision={'kind':'authorization','author':'user','scope':{'item_ids':['US-001']},'source':'Actual fixture request','reason':'Implement'})
        mutate('prepare',iteration_id='ITER-001',increment={'item_ids':['US-001'],'objective':'Book','scope':'Calendar','criteria':['Booking exists'],'required_checks':['unit'],'authorization':'DEC-0001'})
        mutate('start',increment_id='INC-0001');mutate('mark-implemented',increment_id='INC-0001');(self.root/'app.py').write_text('v1')
        mutate('record-evidence',evidence={'increment_id':'INC-0001','check':'unit','result':'passed','scope':'Booking','paths':['app.py']})
        mutate('record-review',review={'increment_id':'INC-0001','decision':'accepted','user_quote':'Accepted fixture result'})
        mapping={'iteration_releases':{'ITER-001':'v0.1.0'},'releases':{'v0.1.0':{'objective':'Booking MVP'}}}
        preview=self.store.migrate(request=mapping);self.store.migrate(True,{**mapping,'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'accepted')
    def test_schema1_preview_is_readonly(self):
        old=engine.Store(self.root);old.transaction({'operation':'initialize','operation_id':'init','purpose':'Old fixture','project':{'name':'Old','purpose':'Booking'}})
        before={p:p.read_bytes() for p in old.directory.rglob('*') if p.is_file()}
        preview=self.store.migrate();self.assertEqual(preview['source_schema'],1)
        self.assertEqual(before,{p:p.read_bytes() for p in old.directory.rglob('*') if p.is_file()})
        self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']});self.assertEqual(self.store.inspect()['schema_version'],3)

    def test_report_context_does_not_grant_acceptance(self):
        self.setup_plan()
        self.op('update-report',iteration_id='ITER-001',document='review',fields={'presented_result':'Draft booking screen'})
        self.assertEqual(self.store.inspect()['reviews'],[])
        with self.assertRaisesRegex(Error,'managed'):
            self.op('update-report',iteration_id='ITER-001',document='review',fields={'reviews':[{'decision':'accepted'}]})
        self.op('update-project',project={'next_step':'Review the screen'})
        self.assertIn('Draft booking screen',(self.store.directory/'release/v0.1.0/ITER-001/review.md').read_text())

    def test_global_quality_policy_is_not_silently_discarded(self):
        with self.assertRaisesRegex(Error,'global'):
            self.op('initialize',project={'name':'Bookly','purpose':'Booking'},quality_policy=['Unit tests'])
        self.assertFalse(self.store.path.exists())

    def test_report_cannot_move_to_another_release(self):
        self.setup_plan()
        self.op('update-release',release={'id':'v0.2.0','objective':'Later booking'})
        self.op('update-report',iteration_id='ITER-001',document='review',fields={'presented_result':'Draft'})
        source=self.store.directory/'release/v0.1.0/ITER-001/review.md'
        target=self.store.directory/'release/v0.2.0/ITER-001/review.md'
        target.parent.mkdir(parents=True);target.write_text(source.read_text())
        with self.assertRaisesRegex(Error,'Report path'):self.store.inspect()

    def test_new_story_baseline_requires_replan_after_refinement(self):
        self.setup_plan();self.authorize()
        self.assertTrue(self.store.inspect()['iterations'][0]['planning_baseline'])
        self.op('update-story',story={'id':'US-0001','purpose':'Select a slot','criteria':['Changed scope']})
        with self.assertRaisesRegex(Error,'baseline changed'):
            self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        self.op('plan-iteration',iteration={'id':'ITER-001','goal':'First booking','scope':'Changed scope'})
        self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Changed scope','authorization':'DEC-0001'})
