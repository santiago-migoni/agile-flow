"""Release scope and alternative disposition regressions."""
import unittest
from scripts import editorial_codec as codec
from scripts.release_store import Error
import test_clean_workflow as workflow

class ReleaseScopeTests(unittest.TestCase):
    setUp=workflow.CleanWorkflow.setUp
    op=workflow.CleanWorkflow.op
    setup_plan=workflow.CleanWorkflow.setup_plan

    def test_structured_scope_links_manual_edits_and_partial_updates(self):
        self.setup_plan()
        rows=[{'item_id':'BL-0001','contribution':'Development only','rationale':'First useful outcome'}]
        self.op('update-release',release={'id':'v0.1.0','scope_items':rows,'scope':['Keep staging outside this delivery']})
        p=self.store.directory/'release/v0.1.0/release-0.1.0.md';text=p.read_text()
        self.assertIn('| [BL-0001](../../backlog/BL-0001.md) | Development only | First useful outcome |',text)
        self.assertIn('## Scope detail\n\nKeep staging outside this delivery',text)
        self.assertEqual(self.store.inspect()['releases'][0]['scope_items'],rows)
        p.write_text(text.replace('Development only','Development with retry')+'\n## Owner notes\n\nKeep this note.\n')
        self.op('update-release',release={'id':'v0.1.0','objective':'Refined objective'})
        self.assertEqual(self.store.inspect()['releases'][0]['scope_items'][0]['contribution'],'Development with retry')
        self.assertEqual(self.store.inspect()['releases'][0]['item_ids'],['BL-0001'])
        self.assertIn('Keep this note.',p.read_text())

    def test_legacy_scope_is_preserved_without_invented_contributions(self):
        data={'release':{'id':'v0.1.0','objective':'First outcome','item_ids':['BL-0001'],'scope':['Development only']}}
        text,schema=codec.render('release','Example',data)
        self.assertEqual(codec.unpack(text,schema),data)
        self.assertIn('| Product need |',text)
        self.assertNotIn('| Release contribution |',text)
        self.assertIn('## Scope detail',text)

    def test_invalid_scope_fails_atomically(self):
        self.setup_plan();good={'item_id':'BL-0001','contribution':'Dev','rationale':'Learn'}
        for rows in [[good,good],[{**good,'item_id':'BL-0099'}],[{**good,'rationale':''}],['BL-0001']]:
            before=self.store.inspect()
            with self.assertRaises(Error):self.op('update-release',release={'id':'v0.1.0','scope_items':rows})
            self.assertEqual(self.store.inspect(),before)
        with self.assertRaises(Error):self.op('update-release',release={'id':'v0.1.0','item_ids':[], 'scope_items':[good]})

    def test_disposition_preserves_knowledge_and_scopes_pending_inventory(self):
        self.setup_plan()
        rows=[{'id':'ALT-1','topic':'Ingress','option':'A','status':'proposed'},
              {'id':'ALT-2','topic':'Ingress','option':'B','status':'proposed','disposition':'deferred','source':'User: later','applicability':'Later release','revisit_when':'After first delivery'},
              {'id':'ALT-3','topic':'Ingress','option':'C','status':'proposed','disposition':'not-selected','source':'Selection of A','applicability':'v0.1.0 only'}]
        self.op('update-architecture',document={'purpose':'Architecture','alternatives':rows})
        before=self.store.inspect();self.assertEqual(before['architecture']['alternatives'],rows)
        summary=(self.store.directory/'summary.md').read_text()
        self.assertIn('1 pending',summary);self.assertNotIn('3 pending',summary)
        self.assertIn('1 deferred or fallback options',summary)
        doc=(self.store.directory/'architecture.md').read_text()
        self.assertIn('## Retained alternatives',doc)
        self.assertIn('Alternatives / ALT-2 /',doc);self.assertNotIn('Alternatives / 2 /',doc)
        for bad in [{**rows[1],'source':''},{**rows[1],'revisit_when':''},{**rows[1],'disposition':'unknown'}]:
            with self.assertRaises(Error):self.op('update-architecture',document={'alternatives':[rows[0],bad]})
        self.assertEqual(self.store.inspect(),before)

    def test_backlog_date_and_stable_render(self):
        self.setup_plan();path=self.store.directory/'backlog/product-backlog.md'
        self.assertNotIn('Updated:** Not recorded',path.read_text())
        before=path.read_text();self.store.render();self.assertEqual(before,path.read_text())

    def test_story_metadata_columns_match_the_template(self):
        self.setup_plan()
        path=self.store.directory/'release/v0.1.0/ITER-001/user-stories/US-0001.md'
        table=[]
        for line in path.read_text().splitlines()+['']:
            if line.startswith('|'):
                table.append(line)
            elif table:
                width=table[0].count('|')
                self.assertTrue(all(row.count('|')==width for row in table),table)
                table=[]
