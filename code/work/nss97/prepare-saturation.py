"""Same 48 Mbps source; change only the selected NSS downlink group to 40 Mbps."""
from pathlib import Path
import hashlib,json
r=Path('work/nss97');prior=Path('work/nss96');p=json.loads((prior/'entry-qualified.json').read_text());checks=[]
for name in [Path(x).name for x in p['sourceManifest']]:
 if name in ('prepare-load.py','session-binding.mjs','run.mjs'):continue
 src=prior/name;dst=r/name;assert not dst.exists(),f'Refuse overwrite {dst}'
 if name in ('fast-path.lua','tag-counter-audit.lua'):dst.write_bytes(src.read_bytes());checks.append({'file':name,'byteIdentical':True});continue
 s=src.read_text(encoding='utf-8');v=s.replace('nss96','nss97').replace('NSS96','NSS97')
 if name=='qos-physical.lua':v=v.replace('60Mbit','40Mbit').replace('59Mbit','39Mbit').replace('60mbit','40mbit').replace('59mbit','39mbit')
 if name=='controlled-session.mjs':v=v.replace('selectedSubgroupCeilingMbps:60','selectedSubgroupCeilingMbps:40')
 if name=='analyze-controlled.py':v=v.replace("'qosParentMbps':60","'qosParentMbps':40")
 back=v.replace('nss97','nss96').replace('NSS97','NSS96')
 if name=='qos-physical.lua':back=back.replace('40Mbit','60Mbit').replace('39Mbit','59Mbit').replace('40mbit','60mbit').replace('39mbit','59mbit')
 if name=='controlled-session.mjs':back=back.replace('selectedSubgroupCeilingMbps:40','selectedSubgroupCeilingMbps:60')
 if name=='analyze-controlled.py':back=back.replace("'qosParentMbps':40","'qosParentMbps':60")
 assert back==s,name;dst.write_text(v,encoding='utf-8');checks.append({'file':name,'namespaceAndSelectedRateLiteralsOnly':True})
q=Path('work/nss84/qualify-qos-native.mjs').read_text(encoding='utf-8').replace('work/nss84','work/nss97').replace("replaceAll('20Mbit','60Mbit').replaceAll('19Mbit','59Mbit')","replaceAll('20Mbit','40Mbit').replaceAll('19Mbit','39Mbit')").replace('60/59/1 Mbps','40/39/1 Mbps')
(r/'qualify-qos-native.mjs').write_text(q,encoding='utf-8')
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss96/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss97/entry-qualified.json')),t=JSON.parse(fs.readFileSync('work/nss97/qos-native-qualification.json'));assert.ok(p.passed&&p.onlySelectedQosBudgetChanged&&p.fastAndTagCounterBytesUnchanged&&p.tcpOfferedMbps===48&&p.qosGroupMbps===40&&t.passed&&t.checks.length===7);assert.equal(t.sourceSha256,crypto.createHash('sha256').update(fs.readFileSync('work/nss97/qos-physical.lua')).digest('hex'));for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
(r/'session-binding.mjs').write_text(binding,encoding='utf-8')
driver=(prior/'run.mjs').read_text(encoding='utf-8').replace('work/nss96/','work/nss97/').replace("root='work/nss96'","root='work/nss97'").replace('NSS96 rate-only 48Mbps','NSS97 selected QoS40 / offered48').replace('qosMbps:60','qosMbps:40');(r/'run.mjs').write_text(driver,encoding='utf-8')
m={f.as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in r.iterdir()if f.is_file()and f.suffix in ('.mjs','.py','.ps1','.lua')}
(r/'entry-qualified.json').write_text(json.dumps({'passed':True,'onlySelectedQosBudgetChanged':True,'fastAndTagCounterBytesUnchanged':True,'qosGroupMbps':40,'tcpOfferedMbps':48,'nativeLifetimesAndOwnedFlowScopesUnchanged':True,'checks':checks,'sourceManifest':m},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'equivalenceChecks':len(checks),'offeredTcpMbps':48,'selectedQosMbps':40,'bulkGuaranteeMbps':39,'rtGuaranteeMbps':1,'bothCeilMbps':40,'fallbackMbps':950,'configurationWrites':False}))
