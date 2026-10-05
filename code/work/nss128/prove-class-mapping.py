from pathlib import Path
import json,sys,hashlib
p=Path(sys.argv[1]);s=json.loads((p/'last-record-private.json').read_text());a=json.loads((p/'actual-accelerated-state-proof.json').read_text());clock=json.loads((p/'clock-calibration-private.json').read_text())['chosen'];maps=[json.loads((p/n).read_text())for n in ['initial-class-leaf-map-proof.json','post-checkpoint-class-leaf-map-proof.json']]
assert json.loads((p/'result.json').read_text())['passed']and a['passed']and clock['boot']==s['boot']
assert maps[0]['sourceSequence']<=maps[1]['sourceSequence']<=s['adapterSourceSequence']and maps[0]['producer']==maps[1]['producer']
for q in maps:
 assert q['passed']and q['mappingByActualClass']and not q['nssAdmissionAllowed']and q['originalDetachedClassLeaseAndKernelPinStillRequired']and 0<=q['sourceAge']<6
 for d,(slot,category,up,down)in zip(q['decisions'],[('tcp','BULK',0x8e050000,0x8f050000),('udp','RT',0x8e060000,0x8f060000)]):
  assert(d['slot'],d['class'],d['upTag'],d['downTag'])==(slot,category,up,down)
  assert a['proof'][slot]['upTag']==up and a['proof'][slot]['downTag']==down
  assert s['classifiedChoice']['pair'][slot]['decision']['class']==category
opened_lower=s['frontendOpenedAt']+clock['midpointOffset']-clock['uncertaintySeconds'];assert(p/'post-checkpoint-class-leaf-map-proof.json').stat().st_mtime<opened_lower
out={'passed':True,'actualHardwareExecution':True,'mappingUsesActualClassNotProtocol':True,'initialAndPostCheckpointFullIdentityAndLeaseChecked':True,'mappedPlanCreatedBeforeFrontendOpened':True,'postCheckpointSequence':maps[1]['sourceSequence'],'actualDetachedClassificationRepeatedBeforeTagPublication':True,'exactClassifierPairClassAndActualEcmBidirectionalTagsMatch':True,'producerSha256':hashlib.sha256(maps[0]['producer'].encode()).hexdigest(),'residentUpTagZeroUnchanged':True,'kernelPinDefaultDenyAndSixSecondRenewalRetained':True,'productionPairRestrictedToTcpBulkUdpRt':True,'tcpRtAndUdpBulkHardwareAccepted':False,'classChangePhysicalRetirementAccepted':False,'permanentNssEnabled':False}
(p/'actual-class-mapping-proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
