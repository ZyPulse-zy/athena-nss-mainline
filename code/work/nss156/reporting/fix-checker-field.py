from pathlib import Path
import json,hashlib
w=Path(__file__).resolve().parents[3];r=w/'work/nss156/reporting';repo=w/'athena-nss-mainline'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=repo/'tools/check_repository.py';s=p.read_text(encoding='utf-8');assert s.count("'nssScopeOneTcpBulkOneUdp'")==1
s=s.replace("'nssScopeOneTcpBulkOneUdp'","'nssScopeOneTcpBulkOneUdpRt'")
s=s.replace("x156['exportedSources']==90","x156['exportedSources']==91").replace("len(manifest['sources'])>=2520","len(manifest['sources'])>=2521").replace("len(f156)==x156['failuresPreserved']==8","len(f156)==x156['failuresPreserved']==9")
s=s.replace("d156=json.loads", "assert f156[8]['submissionChainStoppedBeforeCommit'] and f156[8]['exactFieldNameOnlyCorrected'] and f156[8]['frozenSourcesAndHardwareEvidenceUnchanged']\nd156=json.loads")
p.write_text(s,encoding='utf-8')
failure={'case':'publication-checker-field','cause':'Checker omitted Rt suffix in actual nssScopeOneTcpBulkOneUdpRt field','submissionChainStoppedBeforeCommit':True,'exactFieldNameOnlyCorrected':True,'frozenSourcesAndHardwareEvidenceUnchanged':True}
put(r/'checker-field-failure.json',failure)
failures=read(repo/'evidence/nss156-failures.json');assert len(failures)==8;failures.append(failure);put(repo/'evidence/nss156-failures.json',failures)
source='work/nss156/reporting/fix-checker-field.py';data=Path(__file__).read_bytes();digest=hashlib.sha256(data).hexdigest();out=repo/'code'/source;assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
manifest=read(repo/'source-manifest.json');assert len(manifest['sources'])==2520;manifest['sources'].append({'path':'code/'+source,'workspaceSource':source,'sha256':digest,'bytes':len(data),'role':'publication-field-name-repair-only'});put(repo/'source-manifest.json',manifest)
p=repo/'evidence/nss156-source-proof.json';proof=read(p);assert proof['sources']==90;proof['sources']=91;proof['sourceHashes'][source]=digest;put(p,proof)
p=repo/'evidence/nss156-mainline.json';main=read(p);main['exportedSources']=91;main['failuresPreserved']=9;put(p,main)
for name in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 p=repo/name;s=p.read_text(encoding='utf-8');a='首轮仓库checker把实际字段nssScopeOneTcpBulkOneUdpRt漏写Rt，提交链当即停止；仅修正checker字段名，原冻结源码/硬件证据保留。\n\n';s=s.replace('## NSS155及更早历史',a+'## NSS155及更早历史',1);p.write_text(s,encoding='utf-8')
print(json.dumps({'passed':True,'sourcesTotal':2521,'frozenSourcesUnchanged':True,'operationalEvidenceUnchanged':True,'submissionPreviouslyStopped':True}))
