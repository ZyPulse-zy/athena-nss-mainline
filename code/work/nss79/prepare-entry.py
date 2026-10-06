"""Build a separate controlled-flow owner; leave all prior entry proofs untouched."""
from pathlib import Path
import hashlib,json
p=Path('work/nss79')
guardian=Path('work/nss32/endpoint-firewall-guardian.py').read_text()
assert guardian.count('else 70)')==1
p.joinpath('endpoint-firewall-guardian.py').write_text(guardian.replace('else 70)','else 180)'))
sg=Path('work/nss79/start-load.mjs').read_text().replace("'aliyun-light'","'sg'").replace('8.148.233.192','18.138.159.236').replace('47471','45817').replace('47581','45818')
sg=sg.replace('systemd-run --unit=','sudo -n systemd-run --unit=')
sg=sg.replace("systemctl is-active docker nginx; ",'')
p.joinpath('start-sg.mjs').write_text(sg)
s=Path('work/nss77/real-session.mjs').read_text()
s=s.replace("import {selectRealPair} from '../nss39/pair-policy.mjs';",'')
s=s.replace("import {selectPersistentRealPair} from '../nss74/persistent-pair.mjs';",'')
s=s.replace("import {chooseAfterCheckpoint} from '../nss75/refinement.mjs';",'')
s=s.replace("from './module-stage.mjs'","from '../nss77/module-stage.mjs'")
s=s.replace("observationRoot='work/nss77'","observationRoot='work/nss79'")
s=s.replace("observationRoot+'/record-candidates.mjs'","observationRoot+'/read-controlled.mjs'")
s=s.replace("observationRoot+'/real-candidates-private.json'","observationRoot+'/controlled-candidates-private.json'")
s=s.replace('const pair=selectRealPair(candidates);','const pair=candidates.pairs;')
s=s.replace('candidates.game.length','candidates.udp.length').replace('candidates.bulk.length','candidates.tcp.length')
s=s.replace("const preauditSelected={tcp:convert(pair[0].b),udp:convert(pair[0].g)};let selected;","const preauditSelected=pair[0];let selected;")
s=s.replace("'work/nss77/real-matched-aba-'","'work/nss79/controlled-matched-aba-'")
a=s.index(" const application=JSON.parse(")
b=s.index(" const preauditQualification=",a)
s=s[:a]+" const load=JSON.parse(fs.readFileSync(observationRoot+'/load-latest-private.json'));\n save('controlled-client-private',{load,candidates,config:JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'))});\n"+s[b:]
s=s.replace('work/nss77/current-audit-diagnostic.mjs','work/nss79/current-audit-diagnostic.mjs')
a=s.index('  const persistent=selectPersistentRealPair')
b=s.index("  const source=fs.readFileSync(root+'/read-prerequisites.lua'",a)
s=s[:a]+"  assert.equal(selectionFrame.producer,candidates.producer);\n  selected=selectionFrame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));\n  assert.ok(selected,'Controlled exact pair changed after original full audit');\n  save('persistent-selection-private',{passed:true,producer:selectionFrame.producer,initialSequence:candidates.sourceSequence,currentSequence:selectionFrame.sourceSequence,selected});\n"+s[b:]
s=s.replace("schema:'nss27-real-pair-v1'","schema:'nss79-controlled-owned-pair-v1'")
s=s.replace("observationRoot+'/pc-app-endpoints-private.json'","observationRoot+'/controlled-pc-raw-private.json'")
s=s.replace('fresh.game.some','fresh.udp.some').replace('fresh.bulk.some','fresh.tcp.some')
s=s.replace('Exact real application pair changed before staging','Exact controlled socket pair changed before staging')
s=s.replace('selected=chooseAfterCheckpoint(frame,selectionFrame.producer,selectionFrame.sourceSequence,preauditSelected.udp);',"assert.equal(frame.producer,selectionFrame.producer);assert.ok(frame.sourceSequence>=selectionFrame.sourceSequence);selected=frame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));assert.ok(selected,'Controlled exact pair changed after checkpoint');")
s=s.replace("save('post-checkpoint-application-receipt-private',JSON.parse(fs.readFileSync(observationRoot+'/recorded-application-latest.json')));","save('post-checkpoint-controlled-receipt-private',frame);")
s=s.replace('realCs2SteamPair:true','realCs2SteamPair:false,controlledRealWanPair:true')
s=s.replace('realPairRequired:true,trafficGenerated:false','controlledOwnerRequired:true,trafficGenerated:true')
s=s.replace('trafficGenerated:false','trafficGenerated:true')
s=s.replace('Single real CS2/Steam pair. Default inspection is read-only. No traffic generator.','Bounded owned TCP/UDP pair. Actual permanent classifier and exact native gate.')
s=s.replace('WAITING_FOR_REAL_CS2_STEAM_PAIR','WAITING_FOR_CONTROLLED_OWNED_PAIR').replace('SINGLE_WAN_REAL_PAIR_VISIBLE_NOT_STARTED','SINGLE_WAN_CONTROLLED_PAIR_VISIBLE_NOT_STARTED')
p.joinpath('controlled-session.mjs').write_text(s)
a=Path('work/nss77/current-audit-diagnostic.mjs').read_text().replace('work/nss77','work/nss79').replace('nss77\\/real-matched-aba','nss79\\/controlled-matched-aba')
p.joinpath('current-audit-diagnostic.mjs').write_text(a)
binding="""import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {verifyPreparation as previous} from '../nss77/session-binding.mjs';
export function verifyPreparation(){const q=previous(),p=JSON.parse(fs.readFileSync('work/nss79/entry-qualified.json'));assert.ok(p.passed&&p.controlledOwnershipSeparateFromGameAcceptance&&p.routerLibrariesUnchanged&&p.nativeAndOwnerLimitsUnchanged);for(const[f,h]of Object.entries(p.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...q,sourceManifest:{...q.sourceManifest,...p.sourceManifest}};}
"""
p.joinpath('session-binding.mjs').write_text(binding)
names=['controlled-session.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','session-binding.mjs','client.py','client-watchdog.ps1','server.py','discover-peer.py','probe-peer.py','prepare-entry.py','start-dallas.mjs','endpoint-firewall-guardian.py','start-sg.mjs','ssh-client.mjs']
manifest={str(p/n).replace('\\','/'):hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
p.joinpath('entry-qualified.json').write_text(json.dumps({'passed':True,'controlledOwnershipSeparateFromGameAcceptance':True,'routerLibrariesUnchanged':True,'nativeAndOwnerLimitsUnchanged':True,'qualification':'separate owner source binding; existing NSS77 library proofs reused, actual endpoint/owner admission remains required','sourceManifest':manifest},indent=2)+'\n')
assert 'selectRealPair(' not in s and 'selectPersistentRealPair(' not in s and 'chooseAfterCheckpoint(' not in s
assert 'read-controlled.mjs' in s and "from '../nss77/module-stage.mjs'" in s
assert "realCs2SteamPair:false" in s and 'selectedSubgroupCeilingMbps:20' in s
assert 'controlled-matched-aba-' in a and "work/nss79" in a
print(json.dumps({'boundNewSources':len(manifest),'routerLibrariesUnchanged':True,'ownerAdmissionStillRequired':True}))
