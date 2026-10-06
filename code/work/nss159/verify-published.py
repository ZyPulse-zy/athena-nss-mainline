"""Read actual Git archive, verify remote HEAD, and retain all prior code/evidence."""
from pathlib import Path
import subprocess,tarfile,io,json,hashlib
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss159';base='c28ee23cd45cf89a079c6f1345705e8971c4beb7'
def git(*args,text=False,data=None):return subprocess.check_output(['git',*args],cwd=repo,text=text,input=data)
def tree(ref):return{p.decode():head.decode().split()[2] for item in git('ls-tree','-r','-z',ref,'--','code','evidence').split(b'\0') if item for head,p in [item.split(b'\t',1)]}
commit=git('rev-parse','HEAD',text=True).strip();assert commit==git('ls-remote','origin','refs/heads/main',text=True).split()[0]
blob=git('archive','--format=tar',commit);out=r/('published-'+commit[:12]);out.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:archive.extractall(out,filter='data')
p=subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe','-X','utf8',str(out/'tools/check_repository.py')],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stderr;checked=json.loads(p.stdout)
old,new=tree(base),tree(commit);names=[x for x in old if x!='evidence/current-runtime.json'];assert all(new.get(x)==old[x] for x in names)
data=git('cat-file','--batch',data=('\n'.join(base+':'+x for x in names)+'\n').encode());offset=0
for name in names:
 end=data.index(b'\n',offset);head=data[offset:end].split();assert head[1]==b'blob';size=int(head[2]);start=end+1;assert(out/name).read_bytes()==data[start:start+size];assert data[start+size:start+size+1]==b'\n';offset=start+size+1
assert offset==len(data) and(out/'evidence/nss158-runtime.json').read_bytes()==git('show',base+':evidence/current-runtime.json')
assert json.loads((out/'evidence/current-runtime.json').read_text(encoding='utf-8'))['round']=='NSS159'
manifest=json.loads((out/'source-manifest.json').read_text(encoding='utf-8'));added=manifest['sources'][2687:]
for x in added:assert(out/x['path']).read_bytes()==(w/x['workspaceSource']).read_bytes()
result={'passed':True,'commit':commit,'remoteCommitMatched':True,'actualGitArchiveChecked':True,'baseCommit':base,'historicalGitBlobsRetained':len(names),'old158RuntimeExactGitBytes':True,'newSourcesExactWorkspaceBytes':len(added),'sourceHashesChecked':checked['sourceHashesChecked'],'filesChecked':checked['filesChecked'],'markdownLinksChecked':checked['markdownLinksChecked'],'archiveSha256':hashlib.sha256(blob).hexdigest()}
with(r/'published-git-receipt.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
