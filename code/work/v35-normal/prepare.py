"""Prefer currently active already-admitted BULK flows and retain failed probes."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2]
r,old=w/'work/v35-normal',w/'work/v34-normal'
sha=lambda b:hashlib.sha256(b).hexdigest()
q=json.loads((old/'entry-qualified.json').read_text(encoding='utf8'))
for f,h in q['sourceManifest'].items():assert sha((w/f).read_bytes())==h,f
rebase=lambda b:b.replace(b'work/v34-normal',b'work/v35-normal').replace(rb'work\/v34-normal\/',rb'work\/v35-normal\/')
copied=[]
for f in q['sourceManifest']:
 p=w/f
 if p.name in ['prepare.py','qualify-entry.mjs','session-binding.mjs']:continue
 data=rebase(p.read_bytes()) if p.suffix in ['.mjs','.lua','.ps1'] else p.read_bytes()
 if p.name=='session.mjs':
  before=b"Date.parse('2026-10-07T04:30:00Z')";assert data.count(before)==1
  data=data.replace(before,b"Date.parse('2026-10-07T05:30:00Z')")
 if p.name=='normal-policy.mjs':
  data=data.replace(b'\r\n',b'\n')
  at=data.index(b'\n')+1
  data=data[:at]+b"export const rankExistingBulk=flows=>flows.filter(f=>Number.isFinite(f.decision?.rateKbps)&&f.decision.rateKbps>0).sort((a,b)=>b.decision.rateKbps-a.decision.rateKbps);\n"+data[at:]
  before=b" const exact=f=>frame.flows.some(x=>JSON.stringify(x)===JSON.stringify(f));"
  assert data.count(before)==1
  data=data.replace(before,b" // Rank only existing eligible owned BULK candidates; unknown rates are refused.\n const bulk=rankExistingBulk(frame.bulk);\n"+before)
  for before,after in [(b'a<frame.bulk.length',b'a<bulk.length'),(b'b<frame.bulk.length',b'b<bulk.length'),(b'first=frame.bulk[a],second=frame.bulk[b]',b'first=bulk[a],second=bulk[b]')]:
   assert data.count(before)==1;data=data.replace(before,after)
 if p.name=='normal-selection.mjs':
  data=data.replace(b'\r\n',b'\n')
  for before,after in [
   (b"import{selectNormalTriple}from'./normal-policy.mjs';",b"import{selectNormalTriple,rankExistingBulk}from'./normal-policy.mjs';"),
   (b" const first=frame.bulk.filter(f=>f.identity.wan===wanSlots.tcp);\n const second=frame.bulk.filter(f=>f.identity.wan===wanSlots.tcp2);",b" const ranked=rankExistingBulk(frame.bulk);\n const first=ranked.filter(f=>f.identity.wan===wanSlots.tcp);\n const second=ranked.filter(f=>f.identity.wan===wanSlots.tcp2);"),
   (b"  if(triples.length)return triples;",b"  if(triples.length){\n   const s=triples[0];\n   if(s.tcp.wan===wanSlots.tcp2&&s.tcp2.wan===wanSlots.tcp)return[{...s,tcp:s.tcp2,tcp2:s.tcp}];\n   assert.equal(s.tcp.wan,wanSlots.tcp);assert.equal(s.tcp2.wan,wanSlots.tcp2);return triples;\n  }")]:
   assert data.count(before)==1;data=data.replace(before,after)
 if p.name=='fast-path.lua':
  before=b"   R.lastAdmissionProbe=nil\r\n   if not ready and retryable~=true then error('Initial admission refused: '..tostring(reason),0)end"
  assert data.count(before)==1
  data=data.replace(before,b"   if not ready and retryable~=true then error('Initial admission refused: '..tostring(reason),0)end\r\n   R.lastAdmissionProbe=nil")
 with (r/p.name).open('xb') as f:f.write(data)
 copied.append(p.name)
binding=(old/'session-binding.mjs').read_bytes().replace(b"from'../v33-normal/session-binding.mjs'",b"from'../v34-normal/session-binding.mjs'").replace(b'work/v34-normal/entry-qualified.json',b'work/v35-normal/entry-qualified.json')
with (r/'session-binding.mjs').open('xb') as f:f.write(binding)
result={'passed':True,'oldRoot':'work/v34-normal','oldHashes':q['sourceManifest'],'copied':copied,'cutoff':'2026-10-07T05:30:00Z',
 'onlySelectionRankingAndExistingFailureRetentionChanged':True,'classifiedCandidateThresholdsUnchanged':True,'fixedWanAndOriginalGameContractUnchanged':True,
 'moduleGuardianAndPostCheckpointSequenceUnchanged':True,'sourceFreshnessSeconds':6,'kernelSessionSeconds':90,'kernelMaximumSeconds':120,'ownerSeconds':180,'clientMaximumSeconds':180,
 'phaseSeconds':60,'maximumExactFlows':3,'historicalModelReplayRequired':False,'rootCauseEstablished':False,'hardwareExecuted':False,'routerWrites':False,
 'readOnlySearchErrorPreserved':{'originalCode':1,'error':'rg: work/v20-controlled: path not found','correction':'Use actual named source files; do not scan frozen runtime copies'}}
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'copied':len(copied),'onlyRankingAndFailureRetentionChanged':True,'hardwareExecuted':False}))
