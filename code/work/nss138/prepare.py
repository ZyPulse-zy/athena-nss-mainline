from pathlib import Path
import hashlib,json
old=Path('work/nss137');new=Path('work/nss138');new.mkdir(exist_ok=True)
names=[p for p in old.iterdir() if p.suffix in ('.mjs','.lua','.ps1','.py') and p.name not in ('measure-guardian.mjs','prepare.py')]
for p in names:
 b=p.read_bytes();s=b.replace(b'nss137',b'nss138').replace(b'NSS137',b'NSS138');assert s.replace(b'nss138',b'nss137').replace(b'NSS138',b'NSS137')==b
 if p.name=='qualify.mjs':
  target="const plan=JSON.parse(fs.readFileSync('work/nss135/controlled-class-20261005220728-a0f315c4/stage-plan-private.json')),render="
  replacement="const plan=JSON.parse(fs.readFileSync('work/nss135/controlled-class-20261005220728-a0f315c4/stage-plan-private.json'));for(const k of ['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete plan[k];const render="
  assert s.count(target.encode())==1;s=s.replace(target.encode(),replacement.encode())
 (new/p.name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(new/name).write_bytes((old/name).read_bytes())
failure={'passed':False,'stage':'local whole-guardian transport qualification','error':'Error: Transport length refused','cause':'Qualification replay erroneously included six post-encode audit-only fields; actual runtime plan is saved before those fields are appended.','targetRamSuccessPolicyChecks':11,'endpointStarted':False,'checkpointCreated':False,'productionExperimentWrites':False,'sourceHashes':{str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in names}}
(old/'qualification-failure.json').write_text(json.dumps(failure,indent=2)+'\n',encoding='utf8')
print(json.dumps({'prepared':True,'runtimeBehaviorUnchangedFrom137':True,'onlyQualificationHistoricalPlanShapeCorrected':True,'independentMaximumSeconds':100,'clientMaximumSeconds':180,'productionWrites':False}))
