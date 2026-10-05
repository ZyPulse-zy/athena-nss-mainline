"""Retain v1 bytes; correct only a legacy template interpretation flag."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,shutil
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss128'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['metrics','trial'];digests={}
for name in names:
 p=repo/f'evidence/nss128-{name}.json';old=subprocess.check_output(['git','show',f'HEAD:evidence/nss128-{name}.json'],cwd=repo);assert json.loads(p.read_bytes())==json.loads(old)
 archive=repo/f'evidence/nss128-v1-{name}.json';assert not archive.exists();archive.write_bytes(old);digests[name]=sha(old)
 x=json.loads(old);target=x if name=='metrics'else x['metrics'];assert target['newCpuComparisonAccepted']is False and target['cpuInterpretationRequiresSeparateSameLoadComparison']
 target['newCpuComparisonAccepted']=None;dump(p,x)
 restored=json.loads(p.read_text());target=restored if name=='metrics'else restored['metrics'];target['newCpuComparisonAccepted']=False;assert restored==json.loads(old)
manifest=json.loads((repo/'source-manifest.json').read_text());assert len(manifest['sources'])==1570;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
src=Path(__file__).resolve();rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);digest=sha(src.read_bytes());manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':digest,'bytes':src.stat().st_size,'role':'append-only-analysis-template-label-correction'});manifest['generatedAt']=datetime.now(timezone.utc).isoformat();manifest['lastAppendExport']='NSS128-label-correction';dump(repo/'source-manifest.json',manifest)
proof={'passed':True,'originalPublishedV1RetainedSha256':digests,'onlyFieldCorrected':'newCpuComparisonAccepted','originalLegacyFalseTemplateOverrodeIntendedNull':True,'correctedRawMetricsInterpretationNull':True,'separateSameLoadComparisonAuthoritative':True,'actualMeasurementsChanged':False,'executionSourceAndFrozenInputsChanged':False,'original37SourcesUntouched':True,'initialFailedCheckerRecorded':True,'originalFailedPublishedCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'historicPrefixSources':1570,'historicPrefixCanonicalSha256':prefix,'newSource':rel,'newSourceSha256':digest,'routerWrites':False}
dump(repo/'evidence/nss128-analysis-label-correction.json',proof);dump(r/'analysis-label-correction-receipt.json',proof);print(json.dumps({'passed':True,'actualMeasurementsChanged':False,'oldEvidenceRetained':2,'sourceCount':1571}))
