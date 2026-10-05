"""Keep the qualified 20 s controller; change only the QoS group 40 -> 30."""
from pathlib import Path
import hashlib,json
r=Path('work/nss100');prior=Path('work/nss99');p=json.loads((prior/'entry-qualified.json').read_text());checks=[]
for name in [Path(x).name for x in p['sourceManifest']]:
 if name in ('prepare-long.py','session-binding.mjs','run.mjs','qualify-long.mjs','entry-qualified.json','long-window-qualification.json','qos-native-qualification.json'):continue
 src=prior/name;dst=r/name;assert not dst.exists(),str(dst)
 if name in ('fast-path.lua','tag-counter-audit.lua','module-stage-guardian.lua'):
  dst.write_bytes(src.read_bytes());checks.append({'file':name,'byteIdentical':True});continue
 s=src.read_text(encoding='utf-8');v=s.replace('nss99','nss100').replace('NSS99','NSS100')
 if name=='qos-physical.lua':v=v.replace('40Mbit','30Mbit').replace('39Mbit','29Mbit').replace('40mbit','30mbit').replace('39mbit','29mbit')
 if name=='controlled-session.mjs':v=v.replace('selectedSubgroupCeilingMbps:40','selectedSubgroupCeilingMbps:30')
 if name=='analyze-controlled.py':v=v.replace("'qosParentMbps':40","'qosParentMbps':30")
 if name=='analyze-long.py':v=v.replace("'qosParentMbps':40","'qosParentMbps':30").replace("'qosBytesUnchanged':True","'qosBytesUnchanged':False")
 back=v.replace('nss100','nss99').replace('NSS100','NSS99')
 if name=='qos-physical.lua':back=back.replace('30Mbit','40Mbit').replace('29Mbit','39Mbit').replace('30mbit','40mbit').replace('29mbit','39mbit')
 if name=='controlled-session.mjs':back=back.replace('selectedSubgroupCeilingMbps:30','selectedSubgroupCeilingMbps:40')
 if name=='analyze-controlled.py':back=back.replace("'qosParentMbps':30","'qosParentMbps':40")
 if name=='analyze-long.py':back=back.replace("'qosParentMbps':30","'qosParentMbps':40").replace("'qosBytesUnchanged':False","'qosBytesUnchanged':True")
 assert back==s,name;dst.write_text(v,encoding='utf-8');checks.append({'file':name,'onlyNamespaceAndSelectedRateChanged':True})
(r/'long-window-qualification.json').write_bytes((prior/'long-window-qualification.json').read_bytes())
v=Path('work/nss97/qualify-qos-native.mjs').read_text(encoding='utf-8').replace('nss97','nss100').replace('NSS97','NSS100').replace('40Mbit','30Mbit').replace('39Mbit','29Mbit').replace('40/39/1 Mbps','30/29/1 Mbps')
(r/'qualify-qos-native.mjs').write_text(v,encoding='utf-8')
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss99/session-binding.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss100/entry-qualified.json')),t=JSON.parse(fs.readFileSync('work/nss100/qos-native-qualification.json'));assert.ok(p.passed&&p.onlySelectedQosBudgetChanged&&p.tcpOfferedMbps===48&&p.qosGroupMbps===30&&p.observationTimingUnchanged&&t.passed&&t.checks.length===7);assert.equal(t.sourceSha256,hash(fs.readFileSync('work/nss100/qos-physical.lua')));for(const name of ['fast-path.lua','module-stage-guardian.lua','tag-counter-audit.lua'])assert.equal(hash(fs.readFileSync('work/nss100/'+name)),hash(fs.readFileSync('work/nss99/'+name)));for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(hash(fs.readFileSync(f)),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
(r/'session-binding.mjs').write_text(binding,encoding='utf-8')
v=(prior/'run.mjs').read_text(encoding='utf-8').replace('nss99','nss100').replace('NSS99 20 second phases / QoS40 / offered48','NSS100 20 second phases / QoS30 / offered48').replace('qosMbps:40','qosMbps:30');(r/'run.mjs').write_text(v,encoding='utf-8')
m={f.as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in r.iterdir()if f.is_file()and f.suffix in ('.mjs','.py','.ps1','.lua')}
(r/'entry-qualified.json').write_text(json.dumps({'passed':True,'onlySelectedQosBudgetChanged':True,'tcpOfferedMbps':48,'qosGroupMbps':30,'observationTimingUnchanged':True,'phaseSeconds':20,'fixedNativeSessionSeconds':27,'detachedOwnerSeconds':100,'classifierFreshnessSeconds':6,'checks':checks,'sourceManifest':m},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'files':len(m),'phaseSeconds':20,'selectedQosMbps':30,'bulkGuaranteeMbps':29,'rtGuaranteeMbps':1,'fixedNativeSessionSeconds':27,'routerWrites':False}))
