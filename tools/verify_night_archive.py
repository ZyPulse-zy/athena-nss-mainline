"""Verify the published night tree without changing frozen v1 or v1.1 blobs."""
from pathlib import Path
import argparse,hashlib,io,json,subprocess,tarfile
p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--output',required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];w=Path(a.workspace).resolve();out=Path(a.output).resolve()
base='04408b25209f1cb3bef5a6470460b4a13c7afbb4'
def git(*args,text=False,data=None):return subprocess.check_output(['git',*args],cwd=repo,text=text,input=data)
def tree(ref):
 return {n.decode():h.decode().split()[2] for row in git('ls-tree','-r','-z',ref,'--','code','evidence').split(b'\0') if row for h,n in [row.split(b'\t',1)]}
assert not git('status','--porcelain'),'Uncommitted changes'
commit=git('rev-parse','HEAD',text=True).strip();assert commit==git('ls-remote','origin','refs/heads/main',text=True).split()[0]
blob=git('archive','--format=tar',commit);dest=out/('published-night-'+commit[:12]);dest.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:archive.extractall(dest,filter='data')
check=subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe','-X','utf8',str(dest/'tools/check_repository.py')],capture_output=True,text=True,encoding='utf-8')
with (out/'archive-checker-private.json').open('x',encoding='utf-8') as f:json.dump({'code':check.returncode,'stdout':check.stdout,'stderr':check.stderr},f,indent=2)
assert check.returncode==0,check.stderr;checked=json.loads(check.stdout)
old,new=tree(base),tree(commit);assert all(new.get(n)==h for n,h in old.items())
data=git('cat-file','--batch',data=('\n'.join(base+':'+n for n in old)+'\n').encode());offset=0
for n in old:
 end=data.index(b'\n',offset);head=data[offset:end].split();assert head[1]==b'blob';size=int(head[2]);start=end+1
 assert (dest/n).read_bytes()==data[start:start+size],n
 assert data[start+size:start+size+1]==b'\n';offset=start+size+1
assert offset==len(data)
manifest=json.loads((dest/'source-manifest.json').read_text(encoding='utf-8'));original=json.loads(git('show',base+':source-manifest.json'));assert manifest['sources'][:2825]==original['sources']
new_sources=manifest['sources'][2825:]
for x in new_sources:assert (dest/x['path']).read_bytes()==(w/x['workspaceSource']).read_bytes(),x['path']
hardware=json.loads((dest/'evidence/v13-night-hardware.json').read_text(encoding='utf-8'));assert not hardware['humanGameAcceptance'] and not hardware['permanentNssDeployment']
result={'passed':True,'commit':commit,'remoteCommitMatched':True,'actualGitArchiveChecked':True,'baseCommit':base,'allFrozenV1AndV11CodeEvidenceBlobsPreserved':len(old),'newSourcesExactWorkspaceBytes':len(new_sources),'sourceHashesChecked':checked['sourceHashesChecked'],'filesChecked':checked['filesChecked'],'markdownLinksChecked':checked['markdownLinksChecked'],'archiveSha256':hashlib.sha256(blob).hexdigest(),'actualTwoWanHardwareCompletionClaim':hardware['actualHardwareNssSessionCompleted'],'noNewCpuHumanGameOrPermanentDeploymentClaim':True}
with (out/'published-night-receipt.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
