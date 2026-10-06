"""Check the actual pushed archive, prior Git blobs and all new exact source bytes."""
from pathlib import Path
import subprocess,tarfile,io,json,hashlib
w=Path(__file__).resolve().parents[3];repo=w/'athena-nss-mainline';r=w/'work/nss152/reporting';base='0b0b23c48b7e828701f6f7780522c4becf64592c'
def git(*args,text=False,data=None):return subprocess.check_output(['git',*args],cwd=repo,text=text,input=data)
def tree(ref):return{p.decode():head.decode().split()[2]for e in git('ls-tree','-r','-z',ref,'--','code','evidence').split(b'\0')if e for head,p in[e.split(b'\t',1)]}
commit=git('rev-parse','HEAD',text=True).strip();remote=git('ls-remote','origin','refs/heads/main',text=True).split()[0];assert commit==remote
blob=git('archive','--format=tar',commit);out=r/('published-'+commit[:12]);out.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob))as a:a.extractall(out,filter='data')
p=subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',str(out/'tools/check_repository.py')],capture_output=True,text=True,encoding='utf-8')
if p.returncode:
    (r/'published-check-failure.json').write_text(json.dumps({'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n',encoding='utf-8')
    raise RuntimeError('Archive checker failed; publication chain stopped')
checked=json.loads(p.stdout);old,new=tree(base),tree(commit);names=[p for p in old if p!='evidence/current-runtime.json'];assert all(new.get(p)==old[p]for p in names)
data=git('cat-file','--batch',data=('\n'.join(base+':'+p for p in names)+'\n').encode());offset=0
for name in names:
    end=data.index(b'\n',offset);head=data[offset:end].split();assert head[1]==b'blob';n=int(head[2]);start=end+1;assert(out/name).read_bytes()==data[start:start+n];assert data[start+n:start+n+1]==b'\n';offset=start+n+1
assert offset==len(data);assert(out/'evidence/nss150-runtime.json').read_bytes()==git('show',base+':evidence/current-runtime.json')
assert json.loads((out/'evidence/current-runtime.json').read_text(encoding='utf-8'))['round']=='NSS152'
manifest=json.loads((out/'source-manifest.json').read_text(encoding='utf-8'));new_sources=[v for v in manifest['sources']if v['workspaceSource'].startswith(('work/nss151/','work/nss152/'))]
for v in new_sources:assert(out/v['path']).read_bytes()==(w/v['workspaceSource']).read_bytes()
receipt={'passed':True,'commit':commit,'remoteCommitMatched':True,'actualGitArchiveChecked':True,'baseCommit':base,'historicalGitBlobsRetained':len(names),'old150RuntimeExactGitBytes':True,'newSourcesExactWorkspaceBytes':len(new_sources),'sourceHashesChecked':checked['sourceHashesChecked'],'filesChecked':checked['filesChecked'],'markdownLinksChecked':checked['markdownLinksChecked'],'archiveSha256':hashlib.sha256(blob).hexdigest()}
(r/'published-git-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
