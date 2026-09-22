"""Presentation fidelity and meaning preservation at the reader/writer boundary."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from scripts import clean_markdown, editorial_codec as codec
from scripts.clean_store import CleanStore
from scripts.release_store import Error
import test_clean_workflow as workflow


class EditorialCodecTests(unittest.TestCase):
    def check(self,kind,data):
        text,schema=codec.render(kind,'Synthetic fixture',data)
        self.assertEqual(codec.unpack(text,schema),data)
        self.assertNotIn('<!-- af:',text);self.assertNotIn('{{',text)
        self.assertNotRegex(text,r'(?m)^#{3,} Entry ')
        return text,schema

    def test_nested_roadmap_and_manual_capability_edit(self):
        data={'direction':'Observe before expanding','versions':[{'version':'v0.1.0','stage':'Foundation','intended_outcome':'Persistent workspace','capabilities':['Create workspace','Show status'],'dependencies':['Choose target','Select runtime'],'status':'proposed'}, {'version':'v0.2.0','stage':'Promotion','capabilities':['Test','Promote'],'dependencies':['v0.1.0'],'status':'proposed'}], 'assumptions':['One operator'], 'uncertainties':['Runtime version'],'milestones':['First persistent workspace']}
        text,schema=self.check('roadmap',data)
        self.assertIn('| Version | Stage | Intended outcome | Capabilities | Dependencies | Status |',text)
        self.assertIn('Create workspace<br>Show status',text)
        self.assertEqual(codec.unpack(text.replace('Create workspace<br>Show status','Create workspace<br>Show status<br>Archive workspace'),schema)['versions'][0]['capabilities'],['Create workspace','Show status','Archive workspace'])
        self.assertNotIn('Persistent workspace',json.dumps(schema))
        self.assertIn('| First persistent workspace | Not recorded | Not recorded |',text)

    def test_independent_people_and_success_lists_are_not_joined(self):
        data={'project':{'name':'Demo','purpose':'Coordinate work','users':['Owner'], 'stakeholders':['Sponsor'], 'objectives':['Reduce effort'], 'success_criteria':['A result is observable'], 'confirmed_facts':['One owner'], 'assumptions':['Daily use']},'decisions':[]}
        text,_=self.check('constitution',data)
        self.assertIn('| Owner | Not recorded | Not recorded |',text)
        self.assertIn('| Sponsor | Not recorded | Not recorded |',text)
        self.assertIn('| Reduce effort | Not recorded | Not recorded |',text)
        self.assertIn('| Fact | One owner |',text)
        self.assertIn('| Assumption | Daily use |',text)
        self.assertNotIn('### Purpose',text)

    def test_five_type_specific_blocks_and_structured_requirements(self):
        cases={'US':{'story':{'actor':'Owner','capability':'book a slot','benefit':'avoid calls'}},'NFR':{'quality_attribute':'Latency','applicability':'Schedule','target':'p95 below 200 ms','verification_method':'Load test'},'BUG':{'observed':'Duplicate booking','expected':'One booking','impact':'Calendar conflict','reproduction':['Open calendar','Submit twice']},'TCH':{'technical_objective':'Isolate storage','approach':'Repository boundary','components':['Booking service']},'SPK':{'question':'Which target?','work_limit':'Two hours','expected_output':'Comparison','findings':'Not yet investigated'}}
        for kind,detail in cases.items():
            with self.subTest(kind=kind):
                data={'item':{'id':'US-0001','type':kind,'parent_id':'BL-0001','release_id':'v0.1.0','iteration_id':'ITER-001','state':'open','purpose':'Bounded work','criteria':[{'id':'AC-01','condition':'A valid request','result':'One record'}], 'dod':[{'id':'DOD-01','requirement':'Persistence checked','evidence':'Test output'}],**detail}}
                text,_=self.check('story',data)
                self.assertEqual(re.findall(r'^### (US|NFR|BUG|TCH|SPK) —',text,re.M),[kind])
                self.assertIn('| ID | Condition | Expected result |',text)
                self.assertIn('| ID | Requirement | Evidence required |',text)
                if kind=='US':self.assertIn('As Owner, I want book a slot, so that avoid calls.',text)

    def test_repeated_evidence_and_review_details_keep_actual_sources(self):
        evidence={'evidence':[{'id':'EVD-0001','increment_id':'INC-0001','delivery_revision':1,'check':'Persistence','result':'failed','scope':'Booking','method':'Run check','observed':'No record','limitations':'Local only','at':'2026-09-22'}, {'id':'EVD-0002','increment_id':'INC-0001','delivery_revision':2,'check':'Persistence','result':'passed','scope':'Booking','observed':'One record','limitations':'Local only','at':'2026-09-22'}], 'blockers':[]}
        text,_=self.check('verification',evidence)
        self.assertIn('### EVD-0001 — Persistence',text);self.assertIn('### EVD-0002 — Persistence',text)
        review={'reviews':[{'id':'REV-0001','increment_id':'INC-0001','delivery_revision':2,'decision':'partial','parts':['AC-01','AC-02'],'accepted_parts':['AC-01'],'message_reference':'Synthetic message','user_quote':'Acepto solo AC-01.','evidence_ids':['EVD-0002']}, {'id':'REV-0002','increment_id':'INC-0001','delivery_revision':2,'decision':'deferred','message_reference':'Synthetic later message'}]}
        text,schema=self.check('review',review)
        self.assertIn('> Acepto solo AC-01.',text);self.assertIn('User quotation not recorded',text)
        self.assertNotIn('Acepto',json.dumps(schema))
        with self.assertRaisesRegex(ValueError,'Conflicting repeated'):
            codec.unpack(text.replace('### REV-0001','### REV-0099'),schema)

    def test_unknown_context_special_characters_and_notes(self):
        data={'direction':'A | B & C\nNext line','versions':[], 'extension':{'limits':['a<br>b','x | y'], 'enabled':True,'count':3,'null':None,'nested':{'list':[{'text':'x: y','empty':[]}]} }}
        text,schema=self.check('roadmap',data)
        note='\n## Operator notes\n\nKeep this paragraph.\n\n<details><summary>Details</summary>Literal notes.</details>\n'
        updated,new_schema=clean_markdown.render('roadmap','Synthetic fixture',data,text+note,schema)
        self.assertIn(note.strip(),updated);self.assertEqual(clean_markdown.unpack(updated,new_schema),data)

    def test_literal_empty_labels_whitespace_and_separate_row_details(self):
        self.check('roadmap',{'direction':'  Keep edge spaces  ','assumptions':['No entries'],'extension':{'empty_label':['No entries'],'tab':'\tvalue\t'}})
        data={'versions':[{'version':'v0.1.0','stage':'First','confidence':'Low'},{'version':'v0.2.0','stage':'Second','confidence':'High'}]}
        text,schema=self.check('roadmap',data)
        rows=[line for line in text.splitlines() if line.startswith('| v0.')]
        changed=text.replace(rows[0],'TEMP').replace(rows[1],rows[0]).replace('TEMP',rows[1])
        with self.assertRaisesRegex(ValueError,'identity or order'):codec.unpack(changed,schema)

    def test_all_eleven_sparse_templates(self):
        data={'constitution':{'project':{'name':'Demo','purpose':'Purpose'},'decisions':[]},'roadmap':{'versions':[]},'product_item':{'item':{'id':'BL-0001','purpose':'Need'}},'release':{'release':{'id':'v0.1.0','objective':'First useful outcome'}},'planning':{'iteration':{'id':'ITER-001','goal':'Goal'},'increments':[]},'story':{'item':{'id':'US-0001','type':'US','purpose':'Need','criteria':[],'dod':[]}},'verification':{'evidence':[],'blockers':[]},'review':{'reviews':[]},'retrospective':{'improvements':[]},'summary':{'purpose':'Purpose','next_step':'Discuss outcome'},'product_backlog':{'needs':[],'completed':[]}}
        for kind,value in data.items():
            with self.subTest(kind=kind):self.check(kind,value)
        self.assertNotIn('## MVP definition',self.check('release',data['release'])[0])
        self.assertNotIn('## Git status',self.check('summary',data['summary'])[0])

    def test_actual_template_prose_and_columns_drive_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp);template=(codec.ROOT/'roadmap.md').read_text().replace('| Stage |','| Product stage |').replace('## Major milestones','## Major milestones')
            (target/'roadmap.md').write_text(template)
            with patch.object(codec,'ROOT',target):
                text,schema=self.check('roadmap',{'versions':[{'version':'v0.1.0','stage':'Foundation'}]})
            self.assertIn('| Product stage |',text)
            self.assertEqual(codec.unpack(text,schema)['versions'][0]['stage'],'Foundation')


class EditorialStoreTests(unittest.TestCase):
    setUp=workflow.CleanWorkflow.setUp
    op=workflow.CleanWorkflow.op
    setup_plan=workflow.CleanWorkflow.setup_plan
    authorize=workflow.CleanWorkflow.authorize
    prepare=workflow.CleanWorkflow.prepare

    def test_new_manual_rows_survive_index_only_render(self):
        self.setup_plan();path=self.store.directory/'release/v0.1.0/ITER-001/user-stories/US-0001.md'
        text=path.read_text().replace('| AC-01 | Not recorded | One booking persists |','| AC-01 | Not recorded | One booking persists |\n| AC-02 | Not recorded | Confirmation sent |')
        path.write_text(text);self.store.render()
        self.assertEqual(path.read_text(),text);self.assertEqual(len(self.store.inspect()['stories'][0]['criteria']),2)

    def test_v1_upgrade_is_explicit_previewed_backed_up_and_idempotent(self):
        # Build a published-format fixture using the retained v1 codec, then mark
        # the manifest as that format. No installed plugin or live project is used.
        original=clean_markdown.render
        def v1(kind,title,data,old=None,structure=None,**context):return clean_markdown.render_v1(kind,title,data,old,structure)
        with patch.object(clean_markdown,'render',v1),patch.object(CleanStore,'transaction',lambda obj,r:super(CleanStore,obj).transaction(r)):
            self.setup_plan()
        manifest=self.store.internal/'manifest.json';manifest.write_text(json.dumps({'schema_version':4,'codec':'clean-markdown-v1'}))
        path=self.store.directory/'constitution.md';path.write_text(path.read_text()+'\n## Owner notes\n\nPreserve this clarification.\n')
        before={str(p.relative_to(self.store.directory)):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()}
        self.assertEqual(self.store.inspect()['project']['purpose'],'Book without messages')
        with self.assertRaisesRegex(Error,'upgrade'):self.op('update-project',project={'next_step':'Later'})
        with self.assertRaisesRegex(Error,'Migrate'):self.store.render()
        preview=self.store.migrate()
        self.assertEqual(before,{str(p.relative_to(self.store.directory)):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()})
        self.assertEqual(preview['target_codec'],'editorial-v2')
        result=self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertIn('Preserve this clarification.',path.read_text())
        self.assertEqual(self.store.migrate()['status'],'already_applied')
        for rel,value in before.items():
            if not rel.startswith('.internal/local/'):
                self.assertEqual((self.store.directory/result['backup']/rel).read_bytes(),value)
        self.authorize();self.op('prepare',iteration_id='ITER-001',increment={'item_ids':['US-0001'],'objective':'Book','scope':'Calendar','authorization':'DEC-0001'})
        planning=(self.store.directory/'release/v0.1.0/ITER-001/sprint-planning.md').read_text()
        self.assertIn('### Baseline for INC-0001',planning)
        self.assertIn('| US-0001 | DoD | DOD-01 | Check persistence |',planning)

    def test_v1_upgrade_preserves_acceptance_and_does_not_repair_stale_plan(self):
        def v1(kind,title,data,old=None,structure=None,**context):return clean_markdown.render_v1(kind,title,data,old,structure)
        with patch.object(clean_markdown,'render',v1),patch.object(CleanStore,'transaction',lambda obj,r:super(CleanStore,obj).transaction(r)):
            workflow.legacy.ReleaseWorkflow.test_evidence_acceptance_and_stale_product(self)
        (self.root/'app.py').write_text('v1')
        self.store.internal.joinpath('manifest.json').write_text(json.dumps({'schema_version':4,'codec':'clean-markdown-v1'}))
        path=self.store.directory/'release/v0.1.0/ITER-001/user-stories/US-0001.md'
        path.write_text(path.read_text().replace('One booking persists','One durable booking persists'))
        before=self.store.inspect();baseline=copy.deepcopy(before['iterations'][0]['planning_baseline'])
        self.assertEqual(before['increments'][0]['effective_acceptance'],'accepted')
        preview=self.store.migrate();self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        after=self.store.inspect()
        self.assertEqual(after['increments'][0]['effective_acceptance'],'accepted')
        self.assertEqual(after['iterations'][0]['planning_baseline'],baseline)
        for group in ['evidence','reviews']:
            self.assertEqual(after[group],before[group])

    def test_structured_project_rows_keep_legacy_text_and_do_not_grant_permission(self):
        self.op('initialize',project={'name':'Demo','purpose':'One outcome','users':[{'actor':'Owner','need':'Book','value':'Less coordination'},'Observer'],'confirmed_facts':[{'statement':'One operator','source':'Synthetic user'}],'proposals':[{'statement':'Start small','impact':'Early learning'}]})
        observed=self.store.inspect()
        self.assertEqual(observed['project']['users'][0]['value'],'Less coordination')
        self.assertEqual(observed['decisions'],[])
        self.assertEqual(observed['increments'],[])
        text=(self.store.directory/'constitution.md').read_text()
        self.assertIn('| Owner | Book | Less coordination |',text)

    def test_v1_conversion_preserves_nested_notes(self):
        data={'project':{'name':'Demo','purpose':'One outcome','vision':'Useful product'},'decisions':[]}
        text,schema=clean_markdown.render_v1('constitution','Demo',data)
        text=text.replace('## People and value','### Operator notes\n\nPreserve nested context.\n\n## People and value') if '## People and value' in text else text+'\n### Operator notes\n\nPreserve nested context.\n'
        converted,new_schema=clean_markdown.render('constitution','Demo',data,text,schema)
        self.assertIn('## Operator notes',converted)
        self.assertIn('Preserve nested context.',converted)
        self.assertEqual(clean_markdown.unpack(converted,new_schema),data)

    def test_generated_indexes_have_editorial_tables_and_no_dead_context_links(self):
        self.setup_plan()
        summary=(self.store.directory/'summary.md').read_text();backlog=(self.store.directory/'backlog/product-backlog.md').read_text()
        self.assertIn('| Release | Release objective | Iteration | Iteration goal | Status |',summary)
        self.assertIn('| Order | Product need | Expected value | Status | Target release |',backlog)
        self.assertNotIn('](roadmap.md)',summary)
        self.assertIn('| US | Select a slot | Not estimated |', (self.store.directory/'release/v0.1.0/ITER-001/sprint-planning.md').read_text())
