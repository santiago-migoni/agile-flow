"""Scoped Git operations. Never stage unrelated changes or publish implicitly."""
import os
import hashlib
import json
from pathlib import Path
import subprocess

class GitError(ValueError):pass

class GitWorkflow:
    def __init__(self,root):self.root=Path(root).resolve()
    def run(self,*args,check=True):
        result=subprocess.run(['git','-c','status.relativePaths=false','-C',str(self.root),*args],capture_output=True,text=True,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
        if check and result.returncode:raise GitError(result.stderr.strip() or result.stdout.strip())
        return result.stdout
    def repository(self):
        value=self.run('rev-parse','--show-toplevel',check=False).strip()
        return Path(value) if value else None
    def anchor(self):
        if self.repository() is None:return None
        return {'head':self.run('rev-parse','--verify','HEAD',check=False).strip(),'branch':self.run('symbolic-ref','-q','HEAD',check=False).strip()}
    def status(self):
        repo=self.repository()
        if repo is None:return {'available':False}
        return {'available':True,'repository':str(repo),**self.anchor(),'changes':self.run('status','--porcelain=v1'),'conflicts':self.run('diff','--name-only','--diff-filter=U').splitlines()}
    def ensure_no_conflicts(self):
        if self.repository() and self.run('diff','--name-only','--diff-filter=U').strip():raise GitError('Resolve Git merge conflicts before writing project records.')
    def paths(self,paths):
        repo=self.repository()
        if repo is None:raise GitError('No Git repository. Initialize only with explicit authorization.')
        if not paths:raise GitError('Choose explicit files for the outcome.')
        result=[]
        for value in paths:
            p=self.root/value
            if Path(value).is_absolute() or '..' in Path(value).parts or p.is_symlink() or not p.resolve().is_relative_to(self.root):raise GitError('Commit paths must be concrete project files.')
            if p.is_dir() or '.internal/local' in p.as_posix():raise GitError('Do not commit directories or local recovery data.')
            rel=p.relative_to(repo).as_posix()
            tracked=self.run('ls-files','--full-name','--',':(top,literal)'+rel).strip()
            if not p.exists() and not tracked:raise GitError('Unknown commit path: '+value)
            if p.exists() and not tracked and self.run('check-ignore','--',str(p),check=False).strip():raise GitError('Selected file is ignored; reconcile ignore policy explicitly.')
            result.append(rel)
        return sorted(set(result))
    def preview(self,paths):
        self.ensure_no_conflicts();selected=self.paths(paths);repo=self.repository()
        staged=self.run('diff','--cached','--name-only').splitlines()
        if set(staged)-set(selected):raise GitError('The index contains unrelated staged changes; preserve them before committing this outcome.')
        entries={}
        for path in selected:
            p=repo/path
            entries[path]=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        payload={'anchor':self.anchor(),'paths':selected,'files':entries,'index':self.run('diff','--cached','--binary'),'diff':self.run('diff','HEAD','--',*[':(top,literal)'+p for p in selected],check=False)}
        fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        untracked={}
        for path in selected:
            if not self.run('ls-files','--',':(top,literal)'+path).strip():
                content=(repo/path).read_bytes()
                try:untracked[path]=content.decode('utf-8')
                except UnicodeDecodeError:untracked[path]='Binary file; review separately. SHA-256: '+entries[path]
        return {'status':'preview','fingerprint':fingerprint,**payload,'untracked_content':untracked}
    def commit(self,request,policy):
        permitted=request.get('authorization_source') or (policy.get('commits')=='automatic' and request.get('outcome') in policy.get('outcomes',[]))
        if not permitted:raise GitError('Commit needs an explicit request source or an agreed automatic outcome.')
        if not request.get('message'):raise GitError('Commit message is required.')
        preview=self.preview(request['paths'])
        if request.get('expected_fingerprint')!=preview['fingerprint']:raise GitError('Git preview is stale; inspect the changed files before committing.')
        if not self.anchor()['branch']:raise GitError('Detached HEAD: select the intended branch before committing.')
        # Refuse files changed between preview and staging. Git itself owns the index lock.
        for path,expected in preview['files'].items():
            p=self.repository()/path
            actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
            if actual!=expected:raise GitError('Selected files changed before staging.')
        self.run('add','--',*[':(top,literal)'+p for p in preview['paths']])
        staged=self.run('diff','--cached','--name-only').splitlines()
        if set(staged)-set(preview['paths']) or self.anchor()!=preview['anchor']:raise GitError('Git index or checkout changed before commit; preserve and review the index.')
        # Hooks run normally. Failed hooks leave files and index available for inspection.
        self.run('commit','-m',request['message'])
        return {'status':'applied','commit':self.anchor()['head'],'paths':preview['paths']}
    def initialize(self,request):
        if not request.get('authorization_source'):raise GitError('Git initialization needs explicit authorization.')
        if self.repository():return {'status':'already_applied','repository':str(self.repository())}
        self.run('init');return {'status':'applied','repository':str(self.repository())}
