"""Isolated strategic/operational lifecycle and adoption scenarios."""
import copy
import unittest
from scripts import iterative_lifecycle as cycle
from scripts.release_store import Error
import test_clean_workflow as workflow


class IterativeLifecycleTests(unittest.TestCase):
    setUp = workflow.CleanWorkflow.setUp
    op = workflow.CleanWorkflow.op
    setup_plan = workflow.CleanWorkflow.setup_plan
    authorize = workflow.CleanWorkflow.authorize

    def adopted(self):
        self.setup_plan()
        self.op('adopt-lifecycle', authorization_source='Owner asked to adopt the new cycle')
        self.op('update-release', release={'id':'v0.1.0', 'scope_items':[{'item_id':'BL-0001','contribution':'Create one booking','rationale':'First usable result'}], 'exit_conditions':[{'condition':'Booking usable','evidence':'Owner pilot'}]})
        self.op('commit-release', release_id='v0.1.0', source='Owner agreed booking scope')
        self.op('plan-iteration', iteration={'id':'ITER-001', 'goal':'First booking', 'scope':'Prepared calendar', 'review_access':'Run the local demo with sample credentials; keep it available through review', 'tasks':[{'id':'T1','story':'US-0001','action':'Implement booking','status':'planned'}]})
        self.op('commit-sprint', iteration_id='ITER-001', source='Owner agreed sprint')

    def test_commitments_are_not_execution_permission(self):
        self.adopted()
        before=self.store.inspect()
        self.assertFalse(before['decisions'])
        with self.assertRaises(Error):
            self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        self.assertEqual(before,self.store.inspect())
        self.authorize()
        self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})

    def test_adoption_requires_commitments_before_new_execution(self):
        self.setup_plan();self.authorize()
        self.op('adopt-lifecycle',authorization_source='Owner migration request')
        with self.assertRaisesRegex(Error,'commit release and sprint'):
            self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})

    def test_no_silent_expansion_or_manual_reinterpretation(self):
        self.adopted();before=self.store.inspect()
        for op,fields in [('plan-iteration',{'iteration':{'id':'ITER-001','goal':'More work','scope':'Extra'}}),('update-story',{'story':{'parent_id':'BL-0001','iteration_id':'ITER-001','type':'US','purpose':'Extra','criteria':['Extra'],'dod':['Test']}}),('update-story',{'story':{'id':'US-0001','purpose':'Different meaning'}}),('update-release',{'release':{'id':'v0.1.0','objective':'Extra scope'}})]:
            with self.assertRaises(Error):self.op(op,**fields)
            self.assertEqual(before,self.store.inspect())
        path=self.store.directory/'release/v0.1.0/ITER-001/sprint-planning.md'
        original=path.read_text();path.write_text(original.replace('First booking','Changed goal'))
        with self.assertRaisesRegex(Error,'commitment changed'):self.store.inspect()
        path.write_text(original)
        self.assertEqual(before,self.store.inspect())

    def test_opportunity_is_unassigned_and_progress_does_not_rewrite_plan(self):
        self.adopted();it=copy.deepcopy(self.store.inspect()['iterations'][0])
        self.op('update-backlog',item={'purpose':'Booking reminders','value':'Fewer missed bookings'})
        self.op('record-finding',iteration_id='ITER-001',classification='opportunity',origin='Owner demo',impact='Additional notification behavior',disposition='Prioritize later',backlog_id='BL-0002',source='Owner suggestion')
        self.op('track-task',iteration_id='ITER-001',task_id='T1',status='in_progress',evidence='Booking form implemented, persistence pending',source='Checkout inspection')
        current=self.store.inspect();new=current['iterations'][0]
        self.assertEqual(new['item_ids'],it['item_ids']);self.assertEqual(new['tasks'],it['tasks']);self.assertEqual(new['commitment'],it['commitment'])
        self.assertFalse(current['backlog'][1].get('target_release'))
        path=self.store.directory/'release/v0.1.0/ITER-001/sprint-planning.md'
        text=path.read_text();self.assertIn('## Current task progress',text);self.assertIn('Booking form implemented',text)
        self.assertNotIn('commitment_digest',text);self.assertNotIn('story_digests',text)
        path.write_text(text+'\n## Owner notes\n\nPreserve the demo data.\n')
        self.op('track-task',iteration_id='ITER-001',task_id='T1',status='blocked',evidence='Missing database',source='Runtime observation')
        self.assertIn('Preserve the demo data.',path.read_text())

    def test_interruption_preserves_unfinished_work_and_allows_next_sprint(self):
        self.adopted()
        self.op('update-report',iteration_id='ITER-001',document='review',fields={'unresolved_feedback':'Owner requested reprioritization before implementation'})
        self.op('update-report',iteration_id='ITER-001',document='retrospective',fields={'retain':'Keep goals small; no implementation occurred'})
        with self.assertRaisesRegex(Error,'outstanding'):
            self.op('conclude-sprint',iteration_id='ITER-001',result='completed',reason='Stop',outstanding_story_ids=['US-0001'],source='Owner')
        self.op('conclude-sprint',iteration_id='ITER-001',result='interrupted',reason='Reprioritize',outstanding_story_ids=['US-0001'],source='Owner')
        self.assertEqual(self.store.inspect()['iterations'][0]['state'],'closed')
        self.op('plan-iteration',iteration={'release_id':'v0.1.0','goal':'Finish booking','scope':'Calendar','review_access':'Local demo'})
        self.op('update-story',story={'parent_id':'BL-0001','iteration_id':'ITER-002','follows_up':'US-0001','type':'US','purpose':'Finish slot selection','criteria':['Booking persists'],'dod':['Persistence test']})
        self.op('commit-sprint',iteration_id='ITER-002',source='Owner agreed continuation')
        self.assertEqual(self.store.inspect()['stories'][0]['iteration_id'],'ITER-001')
        self.assertEqual(self.store.inspect()['stories'][1]['follows_up'],'US-0001')

    def test_adoption_preview_stale_and_lossless(self):
        self.setup_plan();path=self.store.directory/'constitution.md';path.write_text(path.read_text()+'\n## Owner notes\n\nOriginal agreements.\n')
        before={str(p):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()}
        report=cycle.preview(self.store)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()})
        result=cycle.adopt(self.store,{'expected_source_fingerprint':'stale','authorization_source':'Owner'})
        self.assertEqual(result['status'],'conflict')
        result=cycle.adopt(self.store,{'expected_source_fingerprint':report['source_fingerprint'],'authorization_source':'Owner'})
        self.assertEqual(result['status'],'applied');self.assertIn('Original agreements.',path.read_text())
        self.assertFalse(self.store.inspect()['iterations'][0].get('commitment'))
        self.assertEqual(cycle.adopt(self.store,{})['status'],'already_applied')

    def test_release_scope_revision_requires_source_and_preserves_sprint(self):
        self.adopted();it=copy.deepcopy(self.store.inspect()['iterations'][0])
        with self.assertRaises(Error):self.op('revise-release',release_id='v0.1.0',fields={'objective':'Revised'},source='Owner')
        self.op('revise-release',release_id='v0.1.0',fields={'objective':'Revised'},impact='Future scope changes, sprint unchanged',source='Owner changed objective')
        now=self.store.inspect();self.assertEqual(now['iterations'][0]['commitment'],it['commitment'])
        self.assertEqual(now['releases'][0]['scope_history'][0]['previous']['objective'],'Booking MVP')
        with self.assertRaises(Error):self.op('assess-release',release_id='v0.1.0',result='completed',outcome='Done',evidence=['Review'],source='Owner',acceptance_source='Owner')
        self.op('assess-release',release_id='v0.1.0',result='incomplete',outcome='Booking pending',evidence=['Sprint plan'],source='Current review')
        self.assertEqual(self.store.inspect()['releases'][0]['fulfillment'],'incomplete')

    def test_interface_design_and_costs_roundtrip(self):
        self.setup_plan()
        self.op('update-project',project={'costs':'Pilot budget only','viability':'Evaluate during pilot'})
        self.op('update-architecture',document={'purpose':'Booking solution','screens':[{'id':'UI-1','screen':'Calendar','actions':'Select slot','status':'proposed'}],'states':[{'id':'ST-1','context':'Calendar','state':'empty','behavior':'Offer next week','status':'proposed'}],'accessibility':[{'id':'A-1','need':'Keyboard access','behavior':'Tab order','status':'proposed'}]})
        text=(self.store.directory/'architecture.md').read_text()
        self.assertIn('## Screens and interactions',text);self.assertIn('Select slot',text)
        self.assertEqual(self.store.inspect()['architecture']['screens'][0]['id'],'UI-1')
        self.assertIn('Pilot budget only',(self.store.directory/'constitution.md').read_text())

    def deliver(self, story='US-0001', iteration='ITER-001', increment='INC-0001'):
        self.op('record-decision',decision={'kind':'authorization','author':'user','reason':'Implement selected story','scope':{'item_ids':[story]},'source':'Owner execution request','quote':'Implement this story.'})
        authorization=self.store.inspect()['decisions'][-1]['id']
        self.op('prepare',iteration_id=iteration,increment={'item_ids':[story],'objective':'Book','scope':'Calendar','authorization':authorization})
        self.op('start',increment_id=increment)
        (self.root/'app.py').write_text('booking works')
        self.op('mark-implemented',increment_id=increment)
        checks=self.store.inspect()['increments'][-1]['required_checks']
        for check in checks:
            self.op('record-evidence',evidence={'increment_id':increment,'check':check,'result':'passed','scope':'Booking','paths':['app.py']})
        self.op('record-review',review={'increment_id':increment,'decision':'accepted','user_quote':'I accept this booking result.'})
        self.op('update-report',iteration_id=iteration,document='retrospective',fields={'retain':'Small bounded demo made review useful'})

    def complete_release(self):
        self.op('assess-release',release_id='v0.1.0',result='completed',outcome='Booking usable',evidence=['Owner pilot'],source='Release review',acceptance_source='Owner accepted release',exit_results=[{'condition':'Booking usable','result':'passed','evidence':'Owner pilot'}],contributions=[{'item_id':'BL-0001','contribution':'Create one booking','result':'delivered','evidence':'Accepted booking demo'}])

    def test_release_completion_without_publication_and_stale_evidence(self):
        self.adopted();self.deliver()
        self.op('conclude-sprint',iteration_id='ITER-001',result='completed',reason='Goal accepted',outstanding_story_ids=[],source='Owner sprint review')
        self.complete_release()
        row=self.store.inspect()['releases'][0]
        self.assertEqual(row['fulfillment'],'completed');self.assertEqual(row['status'],'planned');self.assertFalse(row.get('publication'))
        text=(self.store.directory/'release/v0.1.0/release-0.1.0.md').read_text()
        self.assertIn('Fulfillment assessments',text)
        (self.root/'app.py').write_text('changed behavior')
        self.assertEqual(self.store.inspect()['releases'][0]['effective_fulfillment'],'needs_reassessment')
        with self.assertRaisesRegex(Error,'unfinished or unaccepted'):self.complete_release()
        with self.assertRaisesRegex(Error,'Assess completed fulfillment'):
            self.op('update-release',release={'id':'v0.1.0','status':'released','delivered_outcome':'Booking','publication':{'tag':'v0.1.0'}})

    def test_follow_up_completes_release_without_rewriting_interrupted_history(self):
        self.test_interruption_preserves_unfinished_work_and_allows_next_sprint()
        original=copy.deepcopy(self.store.inspect()['iterations'][0]['closure'])
        self.deliver(story='US-0002',iteration='ITER-002')
        self.op('conclude-sprint',iteration_id='ITER-002',result='completed',reason='Booking accepted',outstanding_story_ids=[],source='Owner review')
        self.complete_release()
        self.assertEqual(self.store.inspect()['iterations'][0]['closure'],original)
        self.assertEqual(original['outstanding_story_ids'],['US-0001'])

    def test_material_finding_blocks_only_dependent_execution_until_resolved(self):
        self.adopted();self.authorize()
        self.op('record-finding',iteration_id='ITER-001',classification='material-change',origin='Architecture investigation',impact='May require another persistence system',disposition='Investigate feasibility',story_id='US-0001',source='Technical investigation')
        request={'iteration_id':'ITER-001','increment':{'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'}}
        with self.assertRaisesRegex(Error,'material finding'):self.op('prepare',**request)
        self.op('resolve-finding',iteration_id='ITER-001',finding_id='FND-001',resolution='Existing persistence supports the agreed behavior; no scope change',disposition='within-scope',source='Bounded investigation result')
        self.op('prepare',**request)

    def test_new_sprint_requires_previous_commitment_conclusion(self):
        self.adopted()
        self.op('plan-iteration',iteration={'release_id':'v0.1.0','goal':'Explore later booking','scope':'Later','review_access':'Local demo'})
        self.op('update-story',story={'parent_id':'BL-0001','iteration_id':'ITER-002','type':'SPK','purpose':'Investigate later work','criteria':['Report'],'dod':['Review findings']})
        with self.assertRaisesRegex(Error,'Conclude the committed sprint'):
            self.op('commit-sprint',iteration_id='ITER-002',source='Owner')

    def test_existing_active_sprint_adopts_without_changing_delivery_baseline(self):
        self.setup_plan();self.authorize()
        self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        self.op('start',increment_id='INC-0001')
        baseline=copy.deepcopy(self.store.inspect()['increments'][0]['story_baseline'])
        self.op('adopt-lifecycle',authorization_source='Owner adoption request')
        self.op('update-release',release={'id':'v0.1.0','scope_items':[{'item_id':'BL-0001','contribution':'Booking','rationale':'Pilot'}],'exit_conditions':[{'condition':'Booking usable'}]})
        self.op('commit-release',release_id='v0.1.0',source='Existing agreed release scope')
        self.op('commit-sprint',iteration_id='ITER-001',source='Existing agreed sprint scope',review_access='Run the local demo')
        self.assertEqual(self.store.inspect()['increments'][0]['story_baseline'],baseline)
        self.op('mark-implemented',increment_id='INC-0001')

    def test_commit_reconciles_draft_story_baseline_and_preserves_story_sentence(self):
        self.setup_plan()
        self.op('update-story',story={'id':'US-0001','purpose':'Select a slot','story':{'actor':'Customer','capability':'Choose a slot','benefit':'Book independently'},'criteria':['One booking persists','Selection is shown']})
        self.op('adopt-lifecycle',authorization_source='Owner')
        self.op('update-release',release={'id':'v0.1.0','scope_items':[{'item_id':'BL-0001','contribution':'Booking','rationale':'Pilot'}],'exit_conditions':[{'condition':'Booking usable'}]})
        self.op('commit-release',release_id='v0.1.0',source='Owner scope agreement')
        self.op('commit-sprint',iteration_id='ITER-001',source='Owner sprint agreement',review_access='Run demo')
        self.authorize()
        self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        with self.assertRaisesRegex(Error,'Committed story definition'):
            self.op('update-story',story={'id':'US-0001','purpose':'Select a slot','story':{'actor':'Another actor','capability':'Change behavior','benefit':'New scope'}})

    def test_uncommitted_empty_draft_cannot_be_declared_completed(self):
        self.setup_plan()
        self.op('adopt-lifecycle',authorization_source='Owner')
        self.op('plan-iteration',iteration={'release_id':'v0.1.0','goal':'Explore future work','scope':'Undecided'})
        with self.assertRaisesRegex(Error,'Commit the sprint'):
            self.op('conclude-sprint',iteration_id='ITER-002',result='completed',reason='Claimed done',outstanding_story_ids=[],source='Owner')
