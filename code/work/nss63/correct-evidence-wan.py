"""Correct offline summary projection from actual selected pairs; no runtime access."""
from pathlib import Path
import json, hashlib, shutil
W=Path(__file__).resolve().parents[2]
def read(p):return json.loads((W/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((W/p).read_bytes()).hexdigest()
def save(p,obj):
    q=W/p;assert not q.exists()
    q.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
a=read('work/nss63/attempts-sanitized.json');changes=[]
for c in a['actualControllerCases']:
    if not c['productionTemporaryStageOccurred']:continue
    p=f"work/{c['round'].lower()}/real-matched-aba-{c['case']}/selected-private.json"
    s=read(p);assert s['tcp']['wan']==s['udp']['wan'] and s['tcp']['mark']==s['udp']['mark']
    wan=s['tcp']['wan'];assert (s['tcp']['mark']>>16)&255==wan
    if c['wan']!=wan:changes.append({'round':c['round'],'case':c['case'],'incorrectV1Wan':c['wan'],'actualWan':wan})
    c.update({'wan':wan,'ctMark':s['tcp']['mark'],'actualSelectedPairSourceSha256':sha(p)})
assert len(changes)==4
a['offlineProjectionCorrection']={'changes':changes,'incorrectWanAfterFallbackRemoved':True,'actualRouterSelectionAndAdmissionUnaffected':True}
save('work/nss63/attempts-v2-sanitized.json',a)
d=read('outputs/nss63-mainline-observations.json');d['actualCases']=a['actualControllerCases']
d['offlineEvidenceCorrection']={'originalV1Sha256':sha('outputs/nss63-mainline-observations.json'),'originalV1RetainedPrivate':True,**a['offlineProjectionCorrection']}
save('outputs/nss63-mainline-observations-v2.json',d)
folder=W/'work/nss63/proof-v2/code';folder.mkdir(parents=True,exist_ok=False)
source='work/nss63/correct-evidence-wan.py';shutil.copyfile(W/source,folder/'correct-evidence-wan.py')
save('work/nss63/source-proof-v2.json',{'sources':1,'sourceHashes':{source:sha(source)},'privateConnectionAndCapturesExcluded':True,'notAdditionalProductionAdmission':True,'role':'offline-evidence-projection-correction-not-runtime'})
print(json.dumps({'correctedCases':4,'allFiveActualSelectedPairsVerified':True,'runtimeChanges':False}))
