import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.document_store import DocumentStore, Error, engine
from scripts import document_store as module, markdown_records as md

class DocumentWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.store=DocumentStore(self.root);self.seq=0
    def mutate(self,operation,**kwargs):
        self.seq+=1
        request=dict(operation=operation,operation_id=f'test-{self.seq}',purpose='Test a sourced requirement.',**kwargs)
        if self.store.path.exists():
            seen=self.store.inspect();request.update(expected_revision=seen['revision'],expected_fingerprint=seen['fingerprint'])
        result=self.store.transaction(request);self.assertEqual(result['status'],'applied',result);return result
    def initialize(self):
        self.mutate('initialize',project={'name':'Bookly','purpose':'Book an appointment.','vision':'Independent booking.','references':['vision.md']})
    def item(self,kind='story',**kwargs):
        self.mutate('update-backlog',item={'type':kind,'purpose':f'{kind} need {self.seq}','criteria':['Book one appointment'],**kwargs})
        return self.store.inspect()['backlog'][-1]['id']
    def plan(self):
        self.initialize();ident=self.item()
        self.mutate('plan-iteration',iteration={'goal':'First booking','scope':'One booking','item_ids':[ident]});return ident
    def prepare(self):
        ident=self.plan();self.mutate('update-dod',document={'criteria':['unit','manual']})
        self.mutate('record-decision',decision={'kind':'authorization','author':'user','reason':'Implement booking','scope':{'item_ids':[ident]},'source':'test message','quote':'Build it.'})
        self.mutate('prepare',iteration_id='ITER-001',increment={'item_ids':[ident],'objective':'First booking','scope':'One booking','criteria':['Book one appointment'],'required_checks':['unit'],'authorization':'DEC-0001'})
    def test_minimal_initialization_and_external_document(self):
        external=self.root/'vision.md';external.write_text('Existing vision');self.initialize()
        self.assertEqual(external.read_text(),'Existing vision')
        self.assertEqual(set(self.store.inventory()),{'constitution.md','summary.md','backlog.md'})
        meta=json.loads(self.store.path.read_text());self.assertNotIn('project',meta);self.assertNotIn('Book an appointment.',json.dumps(meta))
    def test_manual_authored_edits_survive(self):
        self.initialize();p=self.store.directory/'constitution.md'
        p.write_text(p.read_text().replace('Independent booking.','Self-service appointments.')+'\nPersonal note\n')
        self.assertEqual(self.store.inspect()['project']['vision'],'Self-service appointments.')
        self.mutate('update-project',project={'next_step':'Refine cancellation.'})
        self.assertIn('Personal note',p.read_text());self.assertIn('Self-service appointments.',p.read_text())
    def test_manual_generated_edits_preserved(self):
        self.initialize();p=self.store.directory/'backlog.md';p.write_text('Manual priority request\n')
        with self.assertRaisesRegex(Error,'Generated index'):self.item()
        self.assertEqual(p.read_text(),'Manual priority request\n');self.store.render(force=True)
        self.assertEqual(next((self.store.internal/'manual').glob('*')).read_text(),'Manual priority request\n')
    def test_mixed_types_order_and_identity(self):
        self.initialize()
        for kind in ['story','nfr','bug','technical','research']:self.item(kind)
        ids=[x['id'] for x in self.store.inspect()['backlog']]
        self.assertEqual({x.split('-')[0] for x in ids},{'US','NFR','BUG','TECH','SPIKE'})
        self.mutate('reorder-backlog',item_ids=list(reversed(ids)))
        self.mutate('update-backlog',item={'id':ids[0],'purpose':'Renamed need','estimate':3})
        self.assertEqual(len(self.store.inspect()['backlog']),5)
        text=(self.store.directory/'backlog.md').read_text();self.assertLess(text.index(ids[-1]),text.index(ids[0]))
    def test_planning_creates_no_authorization_or_review(self):
        self.plan();seen=self.store.inspect();self.assertEqual(seen['increments'],[]);self.assertEqual(seen['decisions'],[])
        self.assertEqual(seen['iterations'][0]['state'],'draft')
        self.assertFalse((self.store.directory/'iterations/ITER-001/review.md').exists())
    def test_authorization_required(self):
        ident=self.plan();self.mutate('update-dod',document={'criteria':['unit']})
        with self.assertRaises(Error):self.mutate('prepare',iteration_id='ITER-001',increment={'item_ids':[ident],'objective':'Booking','scope':'Booking','criteria':['Booked'],'required_checks':['unit'],'authorization':'DEC-missing'})
        self.assertEqual(self.store.inspect()['increments'],[])
    def test_verification_acceptance_and_new_check(self):
        self.prepare();self.mutate('start',increment_id='INC-0001');file=self.root/'app.py';file.write_text('booking v1')
        self.mutate('mark-implemented',increment_id='INC-0001')
        self.mutate('record-evidence',evidence={'increment_id':'INC-0001','check':'unit','result':'passed','scope':'Booking','paths':['app.py']})
        self.mutate('record-review',review={'increment_id':'INC-0001','decision':'accepted','user_quote':'I accept this booking.'})
        seen=self.store.inspect()['increments'][0];self.assertEqual(seen['effective_verification'],'partial');self.assertEqual(seen['effective_acceptance'],'accepted')
        self.mutate('record-evidence',evidence={'increment_id':'INC-0001','check':'manual','result':'passed','scope':'Booking','paths':['app.py']})
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'accepted')
        file.write_text('booking v2');self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'pending')
    def test_historical_baselines(self):
        self.prepare();before=copy.deepcopy(self.store.inspect()['increments'][0])
        self.mutate('update-dod',document={'criteria':['unit','manual','accessibility']})
        self.mutate('update-backlog',item={'id':'US-001','purpose':'Expanded booking','criteria':['Multiple appointments']})
        after=self.store.inspect()['increments'][0];self.assertEqual(before['document_baseline'],after['document_baseline']);self.assertEqual(after['required_checks'],['unit','manual'])
        snapshots=[json.loads(p.read_text()) for p in (self.store.internal/'transactions').glob('*.json')]
        self.assertTrue(any('definition-of-done.md' in s['source_documents'] for s in snapshots))
    def test_stale_fingerprint(self):
        self.initialize();seen=self.store.inspect();p=self.store.directory/'constitution.md';p.write_text(p.read_text()+'\nNote\n')
        out=self.store.transaction({'operation':'update-project','operation_id':'stale','purpose':'Stale edit','project':{'purpose':'Wrong'},'expected_revision':seen['revision'],'expected_fingerprint':seen['fingerprint']})
        self.assertEqual(out['status'],'conflict')
    def interrupt(self):
        self.initialize();original=module.atomic
        def fail(path,value):
            if path.name=='constitution.md':raise OSError('Simulated interruption')
            return original(path,value)
        with patch.object(module,'atomic',side_effect=fail):
            with self.assertRaises(OSError):self.mutate('update-project',project={'purpose':'Recover this change'})
        self.assertTrue(self.store.pending.exists())
    def test_interruption_recovers_once(self):
        self.interrupt()
        with self.assertRaisesRegex(Error,'Interrupted'):self.store.inspect()
        self.store.recover();self.assertEqual(self.store.inspect()['project']['purpose'],'Recover this change')
        with self.assertRaisesRegex(Error,'No interrupted'):self.store.recover()
    def test_recovery_preserves_conflict(self):
        self.interrupt();p=self.store.directory/'constitution.md';p.write_text(p.read_text()+'User note\n')
        with self.assertRaisesRegex(Error,'Recovery conflict'):self.store.recover()
        self.assertIn('User note',p.read_text())
    def test_read_only_inspection(self):
        self.prepare();before={p:p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()}
        self.store.inspect();self.assertEqual(before,{p:p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()})
    def test_migration_readonly_backup_and_repeat(self):
        legacy=engine.Store(self.root);legacy.transaction({'operation':'initialize','operation_id':'legacy-init','purpose':'Existing project','project':{'name':'Legacy','purpose':'Legacy booking'}})
        p=legacy.views/'vision.md';p.write_text(p.read_text()+'\nManual legacy vision detail\n')
        before={str(p.relative_to(self.store.directory)):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()}
        preview=self.store.migrate();self.assertFalse(self.store.internal.exists())
        self.assertEqual(before,{str(p.relative_to(self.store.directory)):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()})
        self.assertEqual(self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})['status'],'applied')
        for path,content in before.items():self.assertEqual((self.store.internal/'legacy-backup'/path).read_bytes(),content)
        self.assertEqual(self.store.migrate(True)['status'],'already_applied')
    def test_codec_roundtrip_and_patch(self):
        data={'project':{'purpose':'Book **one** appointment\nwith a professional.','criteria':['A','B'],'estimate':None,'enabled':True}}
        text=md.dumps('Example',data)+'\nFree note\n';self.assertEqual(md.loads(text),data)
        data['project']['criteria'].append('C');updated=md.patch(text,data)
        self.assertEqual(md.loads(updated),data);self.assertIn('Free note',updated)
        with self.assertRaises(ValueError):md.loads('Not a structured document')
    def test_multiple_iterations_pause_and_reopen(self):
        self.prepare();self.mutate('start',increment_id='INC-0001')
        self.mutate('pause',target='iteration',iteration_id='ITER-001',reason='User pause')
        self.assertIsNone(self.store.inspect()['active_increment'])
        self.mutate('plan-iteration',iteration={'goal':'Follow-up','scope':'Booking','item_ids':['US-001']})
        self.mutate('prepare',iteration_id='ITER-002',increment={'item_ids':['US-001'],'objective':'Follow-up','scope':'Booking','criteria':['Booked'],'required_checks':['unit'],'authorization':'DEC-0001'})
        self.mutate('start',increment_id='INC-0002')
        with self.assertRaises(Error):self.mutate('resume',increment_id='INC-0001',reason='Resume first')
        self.mutate('close',target='iteration',iteration_id='ITER-002',reason='User cancels',action='cancel')
        self.mutate('reopen',target='iteration',iteration_id='ITER-001',reason='User reopens')
        self.mutate('resume',increment_id='INC-0001',reason='Resume first')
        self.assertEqual(self.store.inspect()['active_increment'],'INC-0001')
    def legacy_mutate(self,legacy,operation,**kwargs):
        state=legacy.read();self.seq+=1
        result=legacy.transaction(dict(operation=operation,operation_id=f'legacy-{self.seq}',purpose='Legacy fixture',expected_revision=state['revision'],expected_fingerprint=engine.state_fingerprint(state),**kwargs))
        self.assertEqual(result['status'],'applied',result)
    def test_migrate_accepted_delivery_and_classify_unknown(self):
        legacy=engine.Store(self.root);legacy.transaction({'operation':'initialize','operation_id':'legacy-init','purpose':'Existing','project':{'name':'Legacy','purpose':'Legacy booking'},'quality_policy':['unit']})
        self.legacy_mutate(legacy,'update-backlog',item={'purpose':'Book appointment','type':'feature'})
        self.legacy_mutate(legacy,'record-decision',decision={'kind':'authorization','author':'user','scope':{'item_ids':['ITEM-0001']},'reason':'Implement','source':'User request'})
        self.legacy_mutate(legacy,'prepare',increment={'item_ids':['ITEM-0001'],'objective':'Book','scope':'Booking','criteria':['Booked'],'required_checks':['unit'],'authorization':'DEC-0001'})
        self.legacy_mutate(legacy,'start',increment_id='INC-0001');self.legacy_mutate(legacy,'mark-implemented',increment_id='INC-0001')
        (self.root/'app.py').write_text('booking')
        self.legacy_mutate(legacy,'record-evidence',evidence={'increment_id':'INC-0001','check':'unit','result':'passed','scope':'Booking','paths':['app.py']})
        self.legacy_mutate(legacy,'record-review',review={'increment_id':'INC-0001','decision':'accepted','user_quote':'Accepted booking'})
        preview=self.store.migrate();self.assertEqual(preview['item_mapping'],{'ITEM-0001':'ITEM-0001'})
        self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'accepted')
        self.mutate('classify-backlog',item_id='ITEM-0001',type='story',reason='User confirmed customer story')
        seen=self.store.inspect();self.assertEqual(seen['increments'][0]['item_ids'],['US-001'])
        self.assertEqual(seen['decisions'][0]['scope']['item_ids'],['US-001'])
        self.assertEqual(seen['increments'][0]['effective_acceptance'],'accepted')
        self.assertEqual(json.loads(self.store.path.read_text())['legacy_item_mapping']['ITEM-0001'],'US-001')
        self.assertTrue((self.store.directory/'backlog/US-001.md').exists())
    def test_retirement_and_duplicate_operation(self):
        self.initialize();ident=self.item();self.mutate('retire-backlog',item_id=ident,reason='No longer needed')
        self.assertEqual(self.store.inspect()['backlog'][0]['state'],'retired')
        request={'operation':'initialize','operation_id':'test-1','purpose':'Test a sourced requirement.','project':{'name':'Bookly','purpose':'Book an appointment.','vision':'Independent booking.','references':['vision.md']}}
        self.assertEqual(self.store.transaction(request)['status'],'already_applied')
        request['project']['name']='Another product'
        with self.assertRaises(Error):self.store.transaction(request)
    def test_legacy_preview_detects_changed_views_before_apply(self):
        legacy=engine.Store(self.root);legacy.transaction({'operation':'initialize','operation_id':'legacy-init','purpose':'Existing','project':{'name':'Legacy','purpose':'Booking'}})
        preview=self.store.migrate();p=legacy.views/'vision.md';p.write_text(p.read_text()+'New manual detail\n')
        with self.assertRaisesRegex(Error,'fingerprint'):self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        current=self.store.migrate();self.assertIn('vision.md',current['manual_view_edits'])
        self.assertFalse(self.store.internal.exists())
    def test_missing_authored_document_does_not_silently_retire_work(self):
        self.initialize();self.item();path=self.store.directory/'backlog/US-001.md';saved=path.read_text();path.unlink()
        with self.assertRaisesRegex(Error,'missing'):self.store.render()
        path.write_text(saved);self.assertEqual(len(self.store.inspect()['backlog']),1)
    def test_planning_baseline_changes_need_explicit_refinement(self):
        self.prepare()
        self.mutate('plan-iteration',iteration={'goal':'Another','scope':'Booking','item_ids':['US-001']})
        self.mutate('update-backlog',item={'id':'US-001','purpose':'Changed scope'})
        with self.assertRaisesRegex(Error,'baseline changed'):self.mutate('prepare',iteration_id='ITER-002',increment={'item_ids':['US-001'],'objective':'Booking','scope':'Booking','criteria':['Booked'],'required_checks':['unit'],'authorization':'DEC-0001'})
    def test_markdown_bullets_and_plan_links(self):
        self.plan();text=(self.store.directory/'iterations/ITER-001/sprint_planning.md').read_text()
        self.assertIn('- US-001',text);self.assertIn('[US-001 criteria](../../backlog/US-001.md#criteria)',text)
        self.assertIn('Planning alone does not authorize execution.',text)
        self.assertIn('planning_baseline',md.loads(text)['iteration'])
        values={'list':['First line\nSecond line','**Another** item']};self.assertEqual(md.loads(md.dumps('Lists',values)),values)
    def test_cli_end_to_end_and_conflict_exit(self):
        import subprocess
        cli=Path(__file__).parents[1]/'scripts/agile_flow.py'
        request={'operation':'initialize','operation_id':'cli-init','purpose':'CLI smoke test','project':{'name':'CLI','purpose':'Test the entry point'}}
        result=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'mutate'],input=json.dumps(request),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'applied')
        request={'operation':'update-project','operation_id':'cli-stale','purpose':'Stale request','expected_revision':0,'expected_fingerprint':'stale','project':{'purpose':'Wrong'}}
        result=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'mutate'],input=json.dumps(request),text=True,capture_output=True)
        self.assertEqual(result.returncode,1);self.assertEqual(json.loads(result.stdout)['status'],'conflict')
    def test_retrospective_is_separate_and_followed_up(self):
        self.plan();self.mutate('record-improvement',iteration_id='ITER-001',improvement={'observation':'Too many technical questions','adjustment':'Investigate reversible choices','target_cycle':'Next planning conversation'})
        self.mutate('follow-up-improvement',improvement_id='IMP-0001',state='applied',effect_evidence='Next planning used a bounded technical investigation.')
        self.assertTrue((self.store.directory/'iterations/ITER-001/retrospective.md').exists())
        self.assertFalse((self.store.directory/'iterations/ITER-001/review.md').exists())
        self.assertEqual(self.store.inspect()['improvements'][0]['state'],'applied')
    def test_decision_table_preserves_quotes_and_structured_scope(self):
        data={'decisions':[{'id':'DEC-0001','kind':'authorization','author':'user','reason':'Build | review','scope':{'item_ids':['US-001']},'source':'message','quote':'Line one\nLine two <br> & more'}]}
        text=md.dumps('Decisions',data)
        self.assertIn('| Id | Kind | Author | Reason | Scope | Source |',text)
        self.assertEqual(md.loads(text),data)
        data['decisions'].append({'id':'DEC-0002','kind':'product','reason':'New choice','supersedes':['DEC-0001']})
        self.assertEqual(md.loads(md.patch(text,data)),data)
    def test_scoped_dod_does_not_require_deployment_for_research(self):
        self.initialize();self.item('research')
        self.mutate('update-dod',document={'criteria':['Document findings'],'scoped_criteria':[{'criterion':'Deploy smoke test','types':['story','bug']}]})
        self.mutate('plan-iteration',iteration={'goal':'Learn','scope':'Bounded investigation','item_ids':['SPIKE-001']})
        self.mutate('record-decision',decision={'kind':'authorization','author':'user','reason':'Investigate','scope':{'item_ids':['SPIKE-001']},'source':'User request'})
        self.mutate('prepare',iteration_id='ITER-001',increment={'item_ids':['SPIKE-001'],'objective':'Learn','scope':'Bounded investigation','criteria':['Answer question'],'required_checks':['Answer question'],'authorization':'DEC-0001'})
        self.assertEqual(self.store.inspect()['increments'][0]['required_checks'],['Answer question','Document findings'])
    def test_manual_history_removal_is_not_silent(self):
        self.initialize();self.mutate('record-decision',decision={'kind':'product','author':'user','reason':'Choose scope','scope':'Booking','source':'User message'})
        p=self.store.directory/'constitution.md';data=md.loads(p.read_text());data['decisions']=[];p.write_text(md.patch(p.read_text(),data))
        with self.assertRaisesRegex(Error,'identities were removed'):self.store.inspect()
