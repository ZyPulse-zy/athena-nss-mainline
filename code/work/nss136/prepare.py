from pathlib import Path
import json
r=Path('work/nss136');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','match-controlled.mjs','ssh-client.mjs','bounded-pacer.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua','tag-normalizer.lua','upload-ack.mjs','upload-server.py','health.mjs','read-final-physical.mjs','classifier.lua','pause-control.mjs','watcher-read.lua']
for name in names:
 b=(Path('work/nss135')/name).read_bytes();s=b.replace(b'nss135',b'nss136').replace(b'NSS135',b'NSS136');assert s.replace(b'nss136',b'nss135').replace(b'NSS136',b'NSS135')==b
 if name=='run.mjs':
  old=b"const baseline=JSON.parse(fs.readFileSync(v.dir+'/udp-baseline-qualified.json'));";assert s.count(old)==1
  s=s.replace(old,b"const preparationRemaining=fs.statSync(v.dir+'/launch-receipt.json').mtimeMs+180000-Date.now();assert.ok(preparationRemaining>150000,'Insufficient original client lifetime for two independent stage epochs');\n const baseline=JSON.parse(fs.readFileSync(v.dir+'/udp-baseline-qualified.json'));")
  old=b"}catch(e){process.exitCode=1;";assert s.count(old)==2
  s=s.replace(old,b"}catch(e){if(started){const l=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),c=JSON.parse(fs.readFileSync(l.dir+'/client-config-private.json')),p=l.dir+'/control.json';const prior=fs.existsSync(p)?JSON.parse(fs.readFileSync(p)):{session:c.session};assert.equal(prior.session,c.session);fs.writeFileSync(p+'.new',JSON.stringify({...prior,stop:true}));fs.renameSync(p+'.new',p);}process.exitCode=1;",1)
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss135')/name).read_bytes())
print(json.dumps({'prepared':True,'sameNativeAndClassificationPolicy':True,'firstWriteRequiresClientRemainingOver150Seconds':True,'noLifetimeExtended':True,'productionWrites':False}))
