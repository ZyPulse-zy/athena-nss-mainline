from pathlib import Path
import json
r=Path('work/nss114');r.mkdir(exist_ok=True)
names=['controlled-session.mjs','current-audit-diagnostic.mjs','match-controlled.mjs','run.mjs','start-dallas.mjs','read-controlled.mjs','close-endpoint.mjs','ssh-client.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','module-stage.mjs','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','fast-path.lua','module-stage-guardian.lua','qos-physical.lua']
for name in names:
 s=(Path('work/nss113')/name).read_bytes();v=s.replace(b'nss113',b'nss114').replace(b'NSS113',b'NSS114');assert v.replace(b'nss114',b'nss113').replace(b'NSS114',b'NSS113')==s
 if name=='module-stage.mjs':
  v=v.replace(b"fs.readFileSync('work/nss49/tag-normalizer.lua'",b"fs.readFileSync('work/nss114/tag-normalizer.lua'").replace(b"fs.readFileSync('work/nss19/normalizer-qualification.json'",b"fs.readFileSync('work/nss114/normalizer-qualification.json'")
 (r/name).write_bytes(v)
for name in ['qos-native-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((Path('work/nss113')/name).read_bytes())
s=Path('work/nss49/tag-normalizer.lua').read_text(encoding='utf-8')
assert s.count("['8f05:0']=2399469568}")==1
s=s.replace("['8f05:0']=2399469568}","['8f05:0']=2399469568,['8e05:0']=0x8e050000,['8e06:0']=0x8e060000}")
old="assert(part.value==0 or part.value==2399535104 or part.value==2399469568,'Unapproved setter')"
assert s.count(old)==1
s=s.replace(old,"local approved={tcp_writer_up=0x8e050000,udp_writer_up=0x8e060000,tcp_writer_down=0x8f050000,udp_writer_down=0x8f060000};local wanted=approved[v.comment:sub(#OWNER+2)];assert(wanted and v.chain=='writer'and part.value==wanted,'Unapproved direction/class setter')")
(r/'tag-normalizer.lua').write_text(s,encoding='utf-8')
print(json.dumps({'prepared':True,'onlyTagNormalizerControlContractChanged':True,'productionWrites':False}))
