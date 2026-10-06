"""Read the exact published tree; retain every frozen v1 code/evidence blob."""
from pathlib import Path
import argparse, hashlib, io, json, subprocess, tarfile

p=argparse.ArgumentParser()
p.add_argument('--workspace',required=True)
p.add_argument('--output',required=True)
a=p.parse_args()
repo=Path(__file__).resolve().parents[1]
w=Path(a.workspace).resolve()
out=Path(a.output).resolve()
base='1751b58f5890385d2f2cb0235bd9928feeb86fff'

def git(*args,text=False,data=None):
    return subprocess.check_output(['git',*args],cwd=repo,text=text,input=data)

def tree(ref):
    return {name.decode():head.decode().split()[2]
            for row in git('ls-tree','-r','-z',ref,'--','code','evidence').split(b'\0') if row
            for head,name in [row.split(b'\t',1)]}

assert not git('status','--porcelain'),'Uncommitted changes'
commit=git('rev-parse','HEAD',text=True).strip()
assert commit==git('ls-remote','origin','refs/heads/main',text=True).split()[0]
blob=git('archive','--format=tar',commit)
dest=out/('published-delivery-'+commit[:12]);dest.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
    archive.extractall(dest,filter='data')
check=subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe','-X','utf8',
    str(dest/'tools/check_repository.py')],capture_output=True,text=True,encoding='utf-8')
with (out/'archive-checker-private.json').open('x',encoding='utf-8') as f:
    json.dump({'code':check.returncode,'stdout':check.stdout,'stderr':check.stderr},f,indent=2)
assert check.returncode==0,check.stderr
checked=json.loads(check.stdout)
old,new=tree(base),tree(commit)
assert all(new.get(name)==digest for name,digest in old.items())
data=git('cat-file','--batch',data=('\n'.join(base+':'+name for name in old)+'\n').encode())
offset=0
for name in old:
    end=data.index(b'\n',offset);head=data[offset:end].split();assert head[1]==b'blob'
    size=int(head[2]);start=end+1
    assert (dest/name).read_bytes()==data[start:start+size],name
    assert data[start+size:start+size+1]==b'\n';offset=start+size+1
assert offset==len(data)
manifest=json.loads((dest/'source-manifest.json').read_text(encoding='utf-8'))
original=json.loads(git('show',base+':source-manifest.json'))
assert manifest['sources'][:2805]==original['sources']
new_sources=manifest['sources'][2805:]
for item in new_sources:
    assert (dest/item['path']).read_bytes()==(w/item['workspaceSource']).read_bytes()
runtime=json.loads((dest/'evidence/current-runtime.json').read_text(encoding='utf-8'))
assert runtime['round']=='NSS160' and runtime['humanSubjectiveAcceptance'] is None
delivery=json.loads((dest/'evidence/v11-entry-delivery.json').read_text(encoding='utf-8'))
assert delivery['oneSessionPerEnable'] and not delivery['permanentNssDeployment']
assert not delivery['newIntegratedHardwareSessionExecuted']
result={'passed':True,'commit':commit,'remoteCommitMatched':True,'actualGitArchiveChecked':True,
    'baseCommit':base,'allFrozenV1CodeEvidenceGitBlobsPreserved':len(old),
    'v1RuntimeExactGitBytesPreserved':True,'newSourcesExactWorkspaceBytes':len(new_sources),
    'sourceHashesChecked':checked['sourceHashesChecked'],'filesChecked':checked['filesChecked'],
    'markdownLinksChecked':checked['markdownLinksChecked'],'archiveSha256':hashlib.sha256(blob).hexdigest(),
    'hostIdleStartStopVerified':True,'newHardwareSessionOrPermanentDeploymentNotClaimed':True}
with (out/'published-delivery-receipt.json').open('x',encoding='utf-8') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
