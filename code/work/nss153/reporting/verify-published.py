"""Verify pushed HEAD, extracted Git archive, old blobs and exact new sources."""
from pathlib import Path
import subprocess,tarfile,io,json,hashlib
w=Path(__file__).resolve().parents[3];repo=w/'athena-nss-mainline';r=w/'work/nss153/reporting';base='81017d2c962712cb2d11817020436a7b9faa5238'
def git(*args,text=False,data=None):return subprocess.check_output(['git',*args],cwd=repo,text=text,input=data)
def tree(ref):return {p.decode():head.decode().split()[2] for item in git('ls-tree','-r','-z',ref,'--','code','evidence').split(b'\0') if item for head,p in [item.split(b'\t',1)]}
commit=git('rev-parse','HEAD',text=True).strip();assert commit==git('ls-remote','origin','refs/heads/main',text=True).split()[0]
blob=git('archive','--format=tar',commit);out=r/('published-'+commit[:12]);out.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:archive.extractall(out,filter='data')
p=subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',str(out/'tools/check_repository.py')],capture_output=True,text=True,encoding='utf-8')
if p.returncode:
    (r/'published-check-failure.json').write_text(json.dumps({'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n',encoding='utf-8');raise RuntimeError('Archive checker failed; publication chain stopped')
checked=json.loads(p.stdout);old,new=tree(base),tree(commit);names=[x for x in old if x!='evidence/current-runtime.json'];assert all(new.get(x)==old[x] for x in names)
data=git('cat-file','--batch',data=('\n'.join(base+':'+x for x in names)+'\n').encode());offset=0
for name in names:
    end=data.index(b'\n',offset);head=data[offset:end].split();assert head[1]==b'blob';size=int(head[2]);start=end+1;assert (out/name).read_bytes()==data[start:start+size];assert data[start+size:start+size+1]==b'\n';offset=start+size+1
assert offset==len(data) and (out/'evidence/nss152-runtime.json').read_bytes()==git('show',base+':evidence/current-runtime.json')
assert json.loads((out/'evidence/current-runtime.json').read_text(encoding='utf-8'))['round']=='NSS153'
manifest=json.loads((out/'source-manifest.json').read_text(encoding='utf-8'));added=[x for x in manifest['sources'] if x['workspaceSource'].startswith('work/nss153/')]
for x in added:assert (out/x['path']).read_bytes()==(w/x['workspaceSource']).read_bytes()
result={'passed':True,'commit':commit,'remoteCommitMatched':True,'actualGitArchiveChecked':True,'baseCommit':base,'historicalGitBlobsRetained':len(names),'old152RuntimeExactGitBytes':True,'newSourcesExactWorkspaceBytes':len(added),'sourceHashesChecked':checked['sourceHashesChecked'],'filesChecked':checked['filesChecked'],'markdownLinksChecked':checked['markdownLinksChecked'],'archiveSha256':hashlib.sha256(blob).hexdigest()}
(r/'published-git-receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
