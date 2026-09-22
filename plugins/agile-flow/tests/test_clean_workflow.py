"""Observable schema-4 behavior and isolated Git integration scenarios."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import test_release_workflow as legacy
from scripts.clean_store import CleanStore
from scripts.release_store import ReleaseStore,Error
from scripts.git_workflow import GitWorkflow,GitError
from scripts import clean_store

class CleanWorkflow(unittest.TestCase):
    setUp=legacy.ReleaseWorkflow.setUp
    op=legacy.ReleaseWorkflow.op
    setup_plan=legacy.ReleaseWorkflow.setup_plan
    authorize=legacy.ReleaseWorkflow.authorize
    prepare=legacy.ReleaseWorkflow.prepare
    def setUp(self):
        legacy.ReleaseWorkflow.setUp(self);self.store=CleanStore(self.root)
    test_all_types=legacy.ReleaseWorkflow.test_all_five_types_share_us_identity
    test_lifecycle=legacy.ReleaseWorkflow.test_evidence_acceptance_and_stale_product
    test_no_permission_from_plan=legacy.ReleaseWorkflow.test_no_authorization_from_plan
    test_dod_baseline=legacy.ReleaseWorkflow.test_story_dod_is_required_and_frozen
    test_story_changes_need_replan=legacy.ReleaseWorkflow.test_new_story_baseline_requires_replan_after_refinement
    test_report_context=legacy.ReleaseWorkflow.test_report_context_does_not_grant_acceptance

    def test_clean_portable_registry(self):
        self.setup_plan()
        for p in self.store.directory.rglob('*.md'):
            if '.internal' not in p.parts:self.assertNotIn('<!-- af:',p.read_text())
        self.assertNotIn('Book without messages',self.store.path.read_text())
        self.assertEqual(self.store.inspect()['schema_version'],4)
        self.assertTrue((self.store.internal/'manifest.json').exists())
        self.assertFalse((self.store.internal/'state.json').exists())
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(self.store.directory,Path(tmp)/'.agile-flow',ignore=shutil.ignore_patterns('local'))
            clone=CleanStore(tmp);before={p:p.read_bytes() for p in clone.directory.rglob('*') if p.is_file()}
            self.assertEqual(clone.inspect()['project']['purpose'],'Book without messages')
            self.assertEqual(before,{p:p.read_bytes() for p in clone.directory.rglob('*') if p.is_file()})

    def test_manual_rows_notes_and_table_spacing(self):
        self.setup_plan();p=self.store.directory/'release/v0.1.0/ITER-001/user-stories/US-0001.md'
        text=p.read_text().replace('| AC-01 | Not recorded | One booking persists |','|AC-01|Not recorded|One booking persists|\n| AC-02 | Not recorded | Customer receives confirmation |')
        text+='\n## Owner notes\n\nKeep the operator workflow available.\n\n<details>\n<summary>Operator context</summary>\nKeep this explanation.\n</details>\n';p.write_text(text)
        self.assertEqual(len(self.store.inspect()['stories'][0]['criteria']),2)
        self.op('update-project',project={'next_step':'Review new criteria'})
        self.assertIn('Keep the operator workflow available.',p.read_text());self.assertIn('<summary>Operator context</summary>',p.read_text())
        self.assertEqual(len(self.store.inspect()['stories'][0]['criteria']),2)

    def test_duplicate_heading_refuses_write(self):
        self.setup_plan();p=self.store.directory/'constitution.md';p.write_text(p.read_text()+'\n## Purpose\n\nAnother purpose\n')
        before=p.read_bytes()
        with self.assertRaisesRegex(ValueError,'duplicate'):self.store.inspect()
        self.assertEqual(before,p.read_bytes())

    def test_schema3_migration_preserves_manual_notes_and_acceptance(self):
        self.store=ReleaseStore(self.root)
        legacy.ReleaseWorkflow.test_evidence_acceptance_and_stale_product(self)
        (self.root/'app.py').write_text('v1')
        p=self.store.directory/'constitution.md';p.write_text(p.read_text()+'\n## Owner notes\n\nPreserve this note.\n')
        originals={str(p.relative_to(self.store.directory)):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()}
        self.store=CleanStore(self.root);preview=self.store.migrate()
        self.assertEqual(originals,{str(p.relative_to(self.store.directory)):p.read_bytes() for p in self.store.directory.rglob('*') if p.is_file()})
        result=self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertEqual(self.store.inspect()['increments'][0]['effective_acceptance'],'accepted')
        self.assertIn('Preserve this note.',p.read_text())
        for rel,data in originals.items():self.assertEqual((self.store.directory/result['backup']/rel).read_bytes(),data)
        self.assertFalse((self.store.internal/'state.json').exists())
        self.assertEqual(self.store.migrate()['status'],'already_applied')

    def test_recover_after_partial_write(self):
        self.setup_plan();original=clean_store.atomic
        # Fail before replay, leaving a valid journal; retry does not repeat the operation.
        with patch.object(self.store,'replay',side_effect=OSError('Interrupted')):
            with self.assertRaises(OSError):self.op('update-project',project={'next_step':'Recovered step'})
        with self.assertRaises(Error):self.store.inspect()
        self.store.recover();self.assertEqual(self.store.inspect()['project']['next_step'],'Recovered step')

    def init_git(self):
        self.store.git.initialize({'authorization_source':'Synthetic fixture'})
        self.store.git.run('config','user.name','Fixture')
        self.store.git.run('config','user.email','fixture@example.invalid')

    def all_records(self):
        return [str(p.relative_to(self.root.resolve())) for p in self.store.directory.rglob('*') if p.is_file() and '.internal/local/' not in str(p)]

    def test_git_complete_snapshot_and_checkout(self):
        self.init_git();self.setup_plan()
        paths=self.all_records();preview=self.store.git_preview({'paths':paths})
        result=self.store.git_commit({'paths':paths,'message':'Initial plan','expected_fingerprint':preview['fingerprint'],'authorization_source':'Fixture request'})
        old=result['commit']
        self.op('update-project',project={'purpose':'Changed purpose'})
        paths=self.all_records();preview=self.store.git_preview({'paths':paths})
        self.store.git_commit({'paths':paths,'message':'Refined plan','expected_fingerprint':preview['fingerprint'],'authorization_source':'Fixture request'})
        self.store.git.run('checkout','--detach',old)
        self.assertEqual(self.store.inspect()['project']['purpose'],'Book without messages')
        self.assertNotIn('.internal/local',self.store.git.run('ls-files'))

    def test_pending_journal_cannot_cross_checkout(self):
        self.init_git();self.setup_plan()
        self.store.git.run('add','.agile-flow');self.store.git.run('commit','-m','Initial fixture')
        with patch.object(self.store,'replay',side_effect=OSError('Interrupted')):
            with self.assertRaises(OSError):self.op('update-project',project={'next_step':'Pending'})
        self.store.git.run('checkout','-b','another-branch')
        with self.assertRaisesRegex(Error,'checkout changed'):self.store.recover()
        self.assertTrue(self.store.pending.exists())

    def test_incomplete_git_snapshot_rejected(self):
        self.init_git();self.setup_plan()
        with self.assertRaisesRegex(Error,'all changed'):
            self.store.git_preview({'paths':['.agile-flow/constitution.md']})

    def test_schema2_migration_to_clean(self):
        old,mutate=legacy.ReleaseWorkflow.legacy_fixture(self)
        request={'iteration_releases':{'ITER-001':'v0.1.0'},'releases':{'v0.1.0':{'objective':'First booking'}}}
        preview=self.store.migrate(request=request)
        self.assertEqual(preview['source_schema'],2)
        self.store.migrate(True,{**request,'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertEqual(self.store.inspect()['stories'][0]['dod'][0]['requirement'],'unit')

    def test_schema1_migration_and_old_writer_refusal(self):
        from scripts.legacy_records import Store
        old=Store(self.root)
        old.transaction({'operation':'initialize','operation_id':'init','purpose':'Fixture','project':{'name':'Legacy','purpose':'Booking'}})
        preview=self.store.migrate();self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertEqual(self.store.inspect()['schema_version'],4)
        self.assertEqual(old.transaction({'operation':'initialize','operation_id':'other','purpose':'Wrong writer','project':{'name':'Legacy','purpose':'Booking'}})['status'],'failed')

    def test_migration_stale_source_rejected(self):
        self.store=ReleaseStore(self.root);self.setup_plan();self.store=CleanStore(self.root)
        preview=self.store.migrate();p=self.store.directory/'constitution.md';p.write_text(p.read_text()+'\n## Notes\nChanged since preview.\n')
        with self.assertRaisesRegex(Error,'fingerprint'):self.store.migrate(True,{'expected_source_fingerprint':preview['source_fingerprint']})
        self.assertFalse(self.store.path.exists())

class GitWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.git=GitWorkflow(self.root)
        self.git.initialize({'authorization_source':'Test fixture instruction'})
        self.git.run('config','user.name','Fixture');self.git.run('config','user.email','fixture@example.invalid')
        (self.root/'initial.txt').write_text('Initial');self.git.run('add','initial.txt');self.git.run('commit','-m','Initial fixture')
    def request(self,paths):
        preview=self.git.preview(paths)
        return {'paths':paths,'message':'Test scoped outcome','expected_fingerprint':preview['fingerprint'],'authorization_source':'Test user request'}
    def test_scoped_commit_preserves_unrelated_unstaged(self):
        (self.root/'a.txt').write_text('A');(self.root/'other.txt').write_text('Other')
        result=self.git.commit(self.request(['a.txt']),{})
        self.assertEqual(self.git.run('show','--format=','--name-only',result['commit']).strip(),'a.txt')
        self.assertIn('other.txt',self.git.status()['changes'])
    def test_unrelated_index_is_preserved(self):
        (self.root/'a.txt').write_text('A');(self.root/'other.txt').write_text('Other');self.git.run('add','other.txt')
        before=self.git.run('diff','--cached','--binary')
        with self.assertRaisesRegex(GitError,'unrelated'):self.git.preview(['a.txt'])
        self.assertEqual(before,self.git.run('diff','--cached','--binary'))
    def test_stale_preview(self):
        (self.root/'a.txt').write_text('A');request=self.request(['a.txt']);(self.root/'a.txt').write_text('B')
        with self.assertRaisesRegex(GitError,'stale'):self.git.commit(request,{})
        self.assertEqual(self.git.run('diff','--cached','--name-only'),'')
    def test_policy(self):
        (self.root/'a.txt').write_text('A');r=self.request(['a.txt']);r.pop('authorization_source');r['outcome']='verified-increment'
        with self.assertRaisesRegex(GitError,'explicit'):self.git.commit(r,{'commits':'on-request'})
        self.assertEqual(self.git.commit(r,{'commits':'automatic','outcomes':['verified-increment']})['status'],'applied')
    def test_failed_hook_preserves_work(self):
        hook=self.root/'.git/hooks/pre-commit';hook.write_text('#!/bin/sh\nexit 1\n');hook.chmod(0o755)
        (self.root/'a.txt').write_text('A');before=self.git.anchor()
        with self.assertRaises(GitError):self.git.commit(self.request(['a.txt']),{})
        self.assertEqual(before,self.git.anchor());self.assertEqual((self.root/'a.txt').read_text(),'A')
    def test_nested_product(self):
        sub=self.root/'product';sub.mkdir();(sub/'a.txt').write_text('A');git=GitWorkflow(sub)
        preview=git.preview(['a.txt']);result=git.commit({'paths':['a.txt'],'message':'Nested product','authorization_source':'Fixture request','expected_fingerprint':preview['fingerprint']},{})
        self.assertEqual(git.run('show','--format=','--name-only',result['commit']).strip(),'product/a.txt')

    def test_initialization_requires_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            git=GitWorkflow(tmp)
            with self.assertRaisesRegex(GitError,'authorization'):git.initialize({})
            self.assertFalse((Path(tmp)/'.git').exists())

    def test_detached_head_refuses_commit(self):
        self.git.run('checkout','--detach','HEAD');(self.root/'a.txt').write_text('A')
        with self.assertRaisesRegex(GitError,'Detached'):self.git.commit(self.request(['a.txt']),{})
