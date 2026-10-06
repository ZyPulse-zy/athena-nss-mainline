"""Bind a sixty-second candidate without changing any historical source."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent
base=root.parents[1]
def read(rel): return (base/rel).read_text(encoding='utf-8')
def write(name,data):
    with (root/name).open('x',encoding='utf-8',newline='\n') as f:f.write(data)
def replace(s,old,new,count=1):
    assert s.count(old)==count,(old,s.count(old),count)
    return s.replace(old,new)

fast=read('work/nss157/fast-path-v2.lua')
for old,new,count in [
 ('R.deadline-55','R.deadline-95',1),
 ('requestedSeconds=20','requestedSeconds=60',1),
 ('s.uptime-start>=20','s.uptime-start>=60',1),
 ('p.seconds>=20 and p.seconds<=21.5','p.seconds>=60 and p.seconds<=61.5',1),
 ('minimumStableSeconds=20','minimumStableSeconds=60',1),
 ('now()+9,deadline-84','now()+9,deadline-124',1),
 ('R.deadline-84','R.deadline-124',1),
 ('R.deadline-56','R.deadline-96',1),
 ('now()+27','now()+90',1),
 ('N/1000-now()>=26','N/1000-now()>=89',1)]:
    fast=replace(fast,old,new,count)
write('fast-path.lua',fast)
proof=json.loads((root/'runtime-elf-comparison.json').read_text())
guardian=read('work/nss158/module-stage-guardian.lua')
guardian=replace(guardian,'now()+100','now()+180')
guardian=replace(guardian,"P.moduleBytes==38480 and P.moduleSha256=='2926791b561bbc90494210f9c77335ece7779f0183bc95457e4ffd9761ca083a'",
                 f"P.moduleBytes=={proof['runtimeBytes']} and P.moduleSha256=='{proof['runtimeSha256']}'")
write('module-stage-guardian.lua',guardian)
payload=replace(read('work/nss157/payload-v4.mjs'),'work/nss157/fast-path-v2.lua','work/v12/fast-path.lua')
write('payload.mjs',payload)
stage=read('work/nss158/module-stage.mjs')
for old,new,count in [
 ('work/nss158/module-stage-guardian.lua','work/v12/module-stage-guardian.lua',1),
 ('work/nss27/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko','work/v12/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko',1),
 ('work/nss27/runtime-elf-comparison.json','work/v12/runtime-elf-comparison.json',1),
 ('work/nss27/endpoint-gate/build-manifest.json','work/v12/endpoint-gate/build-manifest.json',1),
 ('work/nss27/renewal-qualified.json','work/v12/renewal-qualified.json',1),
 ('work/nss158/fast-path.lua','work/v12/fast-path.lua',1)]:
    stage=replace(stage,old,new,count)
write('module-stage.mjs',stage)

for name in ['download-client.mjs','download-server.py','download-policy.mjs',
             'owned-load-policy.mjs','receiver.py','server.py','endpoint-firewall-guardian.py',
             'discover-peer.py','probe-peer.py','client-watchdog.ps1']:
    write(name,read('work/nss159/'+name))
for name in ['read-controlled.mjs','match-controlled.mjs','start-dallas.mjs']:
    source=read('work/nss159/'+name).replace('work/nss159/','work/v12/').replace("'work/nss159'","'work/v12'")
    if name=='start-dallas.mjs':source=replace(source,"const unit='nss159-'","const unit='v12-'")
    write(name,source)
close=read('work/nss159/close-endpoint-v2.mjs').replace('work/nss159/','work/v12/').replace('^nss159-','^v12-')
write('close-endpoint.mjs',close)

audit=read('work/v11/current-audit-diagnostic.mjs').replace('work/v11/','work/v12/').replace('v11\\/','v12\\/')
write('current-audit-diagnostic.mjs',audit)
driver=read('work/nss159/epoch-driver-v4.mjs')
driver=replace(driver,"from '../nss140/declared-baseline.mjs'","from '../nss160/declared-baseline.mjs'")
driver=replace(driver,"from './session-binding-v4.mjs'","from './session-binding.mjs'")
driver=replace(driver,"from '../nss158/module-stage.mjs'","from './module-stage.mjs'")
driver=driver.replace('work/nss159/','work/v12/').replace("'work/nss159'","'work/v12'")
driver=driver.replace('nss159\\/','v12\\/').replace('current-audit-diagnostic-v4.mjs','current-audit-diagnostic.mjs')
driver=replace(driver,"const mode='aba'","const mode='lifecycle'")
driver=replace(driver,"const dir='work/v12/automatic-epoch-'","const dir='work/v12/session-'")
driver=replace(driver,"['abaCompleted','unchangedQoSPlan'","['automaticLifecycleEpochCompleted','unchangedQoSPlan'")
driver=replace(driver,"assert.equal(latest.automaticLifecycleEpochCompleted,false)","assert.equal(latest.abaCompleted,false)")
driver=replace(driver,"['A','B','A2']","['B']")
driver=replace(driver,'p.seconds>=20&&p.seconds<=21.5&&p.sampleCount>=38','p.seconds>=60&&p.seconds<=61.5&&p.sampleCount>=118')
driver=driver.replace('automaticLifecycleEpoch:false,matchedForwardingABA:true','automaticLifecycleEpoch:true,matchedForwardingABA:false')
driver=driver.replace("mode:'aba'","mode:'lifecycle'")
driver=driver.replace('matchedForwardingABARequested:true,matchedForwardingABACompleted:completed&&failures.length===0',
                      'matchedForwardingABARequested:false,matchedForwardingABACompleted:false')
driver=driver.replace('automaticLifecycleEpochCompleted:false,flowEligibilityExitCompleted:',
                      'automaticLifecycleEpochCompleted:completed&&failures.length===0,flowEligibilityExitCompleted:')
driver=replace(driver,'for(let i=0;i<60;i++)','for(let i=0;i<115;i++)')
write('epoch-driver.mjs',driver)
print('Prepared new fixed-session gate/controller and exact owned load; historical sources preserved')
