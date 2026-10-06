"""Verify actual pushed Git archive, source hashes and unchanged old Git blobs."""
from pathlib import Path
import subprocess,tarfile,io,json,hashlib
w=Path(__file__).resolve().parents[3];repo=w/'athena-nss-mainline';r=w/'work/nss150/reporting'
base='b504a8a7afd3024d4d9f807dd688253fa30aceff'
def git(*args,text=False,data=None):return subprocess.check_output(['git',*args],cwd=repo,text=text,input=data)
def tree(ref):
    return {p.decode():head.decode().split()[2] for entry in git('ls-tree','-r','-z',ref,'--','code','evidence').split(b'\0') if entry for head,p in [entry.split(b'\t',1)]}
commit=git('rev-parse','HEAD',text=True).strip();remote=git('ls-remote','origin','refs/heads/main',text=True).split()[0];assert commit==remote
blob=git('archive','--format=tar',commit);out=r/('published-'+commit[:12]);out.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob)) as a:a.extractall(out,filter='data')
check=subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',str(out/'tools/check_repository.py')],capture_output=True,text=True,encoding='utf-8')
if check.returncode:
    (r/'published-check-failure.json').write_text(json.dumps({'code':check.returncode,'stdout':check.stdout,'stderr':check.stderr},indent=2)+'\n',encoding='utf-8')
    raise RuntimeError('Actual published archive checker failed; release chain stopped')
proof=json.loads(check.stdout);old,current=tree(base),tree(commit)
names=[p for p in old if p!='evidence/current-runtime.json'];assert all(current.get(p)==old[p] for p in names)
data=git('cat-file','--batch',data=('\n'.join(base+':'+p for p in names)+'\n').encode());offset=0
for p in names:
    end=data.index(b'\n',offset);head=data[offset:end].split();assert head[1]==b'blob';n=int(head[2]);start=end+1
    assert (out/p).read_bytes()==data[start:start+n],p;assert data[start+n:start+n+1]==b'\n';offset=start+n+1
assert offset==len(data)
assert (out/'evidence/nss148-runtime.json').read_bytes()==git('show',base+':evidence/current-runtime.json')
assert json.loads((out/'evidence/current-runtime.json').read_text(encoding='utf-8'))['round']=='NSS150'
manifest=json.loads((out/'source-manifest.json').read_text(encoding='utf-8'))
new_sources=[v for v in manifest['sources'] if v['workspaceSource'].startswith(('work/nss149/','work/nss150/'))]
for v in new_sources:assert (out/v['path']).read_bytes()==(w/v['workspaceSource']).read_bytes()
receipt={'passed':True,'commit':commit,'remoteCommitMatched':True,'actualGitArchiveChecked':True,
 'baseCommit':base,'historicalGitBlobsRetained':len(names),'old148RuntimeExactGitBytesRetained':True,
 'newSourcesExactWorkspaceBytes':len(new_sources),'sourceHashesChecked':proof['sourceHashesChecked'],
 'filesChecked':proof['filesChecked'],'markdownLinksChecked':proof['markdownLinksChecked'],
 'archiveSha256':hashlib.sha256(blob).hexdigest()}
(r/'published-git-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
