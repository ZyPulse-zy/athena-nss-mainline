from pathlib import Path
import json
r=Path('work/nss135');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','health.mjs','read-final-physical.mjs','classifier.lua','pause-control.mjs']
for name in names:
 b=(Path('work/nss133')/name).read_bytes();s=b.replace(b'nss133',b'nss135').replace(b'NSS133',b'NSS135');assert s.replace(b'nss135',b'nss133').replace(b'NSS135',b'NSS133')==b
 if name=='pause-control.mjs':
  a=s.index(b' const code=`');z=s.index(b'`;\n try{',a)+2
  s=s[:a]+b" const code=fs.readFileSync('work/nss135/watcher-read.lua','utf8');"+s[z:]
  old=b"if(v.count===2&&v.stop===0)";assert s.count(old)==1;s=s.replace(old,b"if(v.count===2&&v.stop===0&&v.stopAfter===0)")
  old=b"assert.ok(v.count===0||v.count===1,'Unexpected pretrigger ECM count');";assert s.count(old)==1;s=s.replace(old,b"assert.ok(v.count>=0&&v.count<=2,'Unexpected pretrigger ECM scope');if(v.count>0)assert.equal(v.hash,context.plan.frozenHash);")
  old=b" }finally{c.close()}";assert s.count(old)==1;s=s.replace(old,b" }catch(e){fs.writeFileSync(context.dir+'/pause-watcher-error-private.json',JSON.stringify({error:String(e),readings:reads},null,2)+'\\n',{flag:'wx'});throw e;}finally{c.close()}")
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss133')/name).read_bytes())
print(json.dumps({'prepared':True,'fix':'Counter reader returns one value; stop sampled before and after; watcher failures retained','nativeAndRetirementPolicyUnchanged':True,'productionWrites':False}))
