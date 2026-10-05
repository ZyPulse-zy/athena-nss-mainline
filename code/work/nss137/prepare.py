from pathlib import Path
import json
r=Path('work/nss137');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','health.mjs','read-final-physical.mjs','classifier.lua','pause-control.mjs','watcher-read.lua']
for name in names:
 b=(Path('work/nss136')/name).read_bytes();s=b.replace(b'nss136',b'nss137').replace(b'NSS136',b'NSS137');assert s.replace(b'nss137',b'nss136').replace(b'NSS137',b'NSS136')==b
 if name=='module-stage-guardian.lua':
  old=b'  while now()<deadline-1 do n.nanosleep(0,100000000);stopped()end';assert s.count(old)==1
  new=b"""  local ending=deadline-1
  if record.classChangeTestCompleted or record.freshEpochRelearningCompleted then
   for _,key in ipairs({'moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'})do assert(record[key]==true,'Success teardown incomplete: '..key)end
   stopped();absent('/sys/module/'..MOD);absent('/sys/module/qca_nss_qdisc')
   record.successEarlyCompletion=true;record.successRecordGraceSeconds=5;store();ending=math.min(ending,now()+5)
  end
  while now()<ending do n.nanosleep(0,100000000);stopped()end"""
  s=s.replace(old,new)
 if name=='run.mjs':
  old=b'preparationRemaining>150000';assert s.count(old)==1;s=s.replace(old,b'preparationRemaining>100000')
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss136')/name).read_bytes())
print(json.dumps({'prepared':True,'successOnlyEndsAfterVerifiedCompleteRestorationAndFiveSecondReceiptGrace':True,'failureOriginalIndependent100SecondDeadlineUnchanged':True,'clientOriginal180SecondLimitUnchanged':True,'productionWrites':False}))
