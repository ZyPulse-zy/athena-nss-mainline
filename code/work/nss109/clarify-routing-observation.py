"""Correct an ambiguous v1 field without overwriting the original evidence."""
from pathlib import Path
import json,hashlib,shutil
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=repo/'evidence/nss109-path-localization.json';data=json.loads(old.read_text(encoding='utf-8'));assert data['identity'].pop('routerPbrOrNatChanged')is False
data['identity'].update({'experimentChangedPbrOrNat':False,'naturalWan4FailoverObservedAndIndependentlyProved':True,'pbrTransitionTimingWithinCaptureWindowsMeasured':False,'noClaimThatAllRuntimePbrWasUnchanged':True})
new=repo/'evidence/nss109-path-localization-v2.json';assert not new.exists();dump(new,data)
src=Path(__file__);rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();shutil.copyfile(src,dst)
mp=repo/'source-manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'));assert len(manifest['sources'])==1185
prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode());manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(src.read_bytes()),'bytes':src.stat().st_size,'role':'clarify-runtime-PBR-observation-with-v1-retained'});dump(mp,manifest)
proof={'metadataCorrectionOnly':True,'oldV1EvidenceRetained':True,'oldV1Sha256':sha(old.read_bytes()),'newV2Sha256':sha(new.read_bytes()),'countsAndRawSequenceEvidenceUnchanged':True,'ambiguousField':'routerPbrOrNatChanged','correctMeaning':'No experimental PBR/NAT writes; existing automatic WAN4 failover was observed; its timing inside the capture windows was not sampled','newSource':rel,'newSourceSha256':sha(src.read_bytes()),'prior1185SourcePrefixSha256':prefix}
dump(repo/'evidence/nss109-routing-clarification.json',proof)
for name in ['STATE.md','ARTIFACT_INDEX.md','EXPERIMENT_LOG.md']:
 p=repo/'docs'/name;p.write_text(p.read_text(encoding='utf-8').replace('../evidence/nss109-path-localization.json','../evidence/nss109-path-localization-v2.json'),encoding='utf-8')
p=repo/'evidence/current-runtime.json';runtime=json.loads(p.read_text(encoding='utf-8'));runtime['pathLocalizationReference']='evidence/nss109-path-localization-v2.json';runtime['routingObservationMetadataClarifiedWithoutNewTrial']=True;dump(p,runtime)
dump(w/'work/nss109/routing-clarification.json',proof);print(json.dumps({'metadataClarified':True,'oldEvidenceRetained':True,'totalSources':1186,'newExperiment':False}))
