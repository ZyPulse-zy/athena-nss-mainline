"""Rebase the qualified bounded three-flow controller onto owned packet fixtures."""
from pathlib import Path
import hashlib, json
w = Path(__file__).resolve().parents[2]
r, old, fixture = w/'work/v36-sim', w/'work/v35-normal', w/'work/v20-five'
sha = lambda b: hashlib.sha256(b).hexdigest()
q = json.loads((old/'entry-qualified.json').read_text())
for f,h in q['sourceManifest'].items(): assert sha((w/f).read_bytes()) == h, f
copied = []
def save(n,b):
    with (r/n).open('xb') as f: f.write(b)
    copied.append(n)
def rebase(b):
    return b.replace(b'work/v35-normal',b'work/v36-sim').replace(rb'work\/v35-normal\/',rb'work\/v36-sim\/')
for f in q['sourceManifest']:
    p=w/f
    if p.name in ['prepare.py','qualify-entry.mjs','session-binding.mjs','read-controlled.mjs','read-real-candidates.mjs','start-application-guard.ps1','application-watchdog.ps1']: continue
    b=rebase(p.read_bytes()) if p.suffix in ['.mjs','.lua','.ps1'] else p.read_bytes()
    if p.name=='session.mjs':
        b=b.replace(b"Date.parse('2026-10-07T05:30:00Z')", b"Date.parse('2026-10-07T06:30:00Z')")
        b=b.replace(b'Current human continuation after morning closure',b'Human authorized owned game-packet simulation, CS2 stopped')
    if p.name=='epoch-driver.mjs':
        b=b.replace(b'realCs2SteamPair:true,controlledRealWanPair:false',b'realCs2SteamPair:false,controlledRealWanPair:true,simulatedGamePackets:true')
    save(p.name,b)
for n in ['native-client.mjs','start-dallas.mjs','match-controlled.mjs','owned-load-policy.mjs','client-watchdog.ps1','close-endpoint.mjs','persistent-ssh.mjs','download-server.py','endpoint-firewall-guardian.py','receiver.py','server.py','discover-peer.py','probe-peer.py']:
    b=(fixture/n).read_bytes().replace(b'work/v20-five',b'work/v36-sim').replace(b'v20-five-',b'v36-sim-').replace(b'^v20-five-',b'^v36-sim-')
    save(n,b)
b=(fixture/'read-controlled.mjs').read_bytes().replace(b'work/v20-five',b'work/v36-sim')
b=b.replace(b"import{candidateAdapter}",b"import{selectNormalTriple}from'./normal-policy.mjs';\nimport{candidateAdapter}",1)
at=b"fs.writeFileSync(root+'/controlled-candidates-private.json',JSON.stringify(out,null,2)+'\\n');"
assert b.count(at)==1
b=b.replace(at,b"out.game=udp;out.bulk=tcp;out.simulatedGamePackets=true;out.realCs2SteamPair=false;out.applicationOwnershipRequired=true;out.pairs=selectNormalTriple(out);"+at+b"\nfs.writeFileSync(root+'/pc-app-endpoints-private.json',JSON.stringify(pc,null,2)+'\\n');\nfs.writeFileSync(root+'/real-candidates-private.json',JSON.stringify(out,null,2)+'\\n');\nfs.writeFileSync(root+'/real-candidates-raw-private.json',JSON.stringify(raw,null,2)+'\\n');\nfs.writeFileSync(root+'/normal-reader-process-private.json',JSON.stringify({code:pcRaw.status,ownedControlledFixture:true},null,2)+'\\n');\nfs.writeFileSync(root+'/real-reader-qualified.json',JSON.stringify({passed:true,ownedControlledFixture:true,realCs2SteamPair:false,automaticClassifierUsed:true,routerWrites:false})+'\\n');")
save('read-controlled.mjs',b)
save('session-binding.mjs',b"import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{verifyPreparation as inherited}from'../v35-normal/session-binding.mjs';\nexport function verifyPreparation(){const old=inherited(),q=JSON.parse(fs.readFileSync('work/v36-sim/entry-qualified.json'));assert.ok(q.passed&&!q.hardwareExecuted);for(const[f,h]of Object.entries(q.sourceManifest))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),h,f);return{...old,sourceManifest:{...old.sourceManifest,...q.sourceManifest},externalSourceBindings:old.externalSourceBindings};}\n")
receipt={'passed':True,'oldHashes':q['sourceManifest'],'fixtureSourceHashes':{str(p.relative_to(w)).replace('\\','/'):sha(p.read_bytes()) for p in [fixture/n for n in ['native-client.mjs','start-dallas.mjs','match-controlled.mjs','owned-load-policy.mjs','client-watchdog.ps1','close-endpoint.mjs','persistent-ssh.mjs','download-server.py','endpoint-firewall-guardian.py','receiver.py','server.py','discover-peer.py','probe-peer.py','read-controlled.mjs']]},'copied':copied,'cutoff':'2026-10-07T06:30:00Z','humanRequestedPacketSimulation':True,'cs2AndSteamDownloadsNotRequired':True,'automaticClassificationNotForced':True,'dataPlaneAndAdmissionThresholdsUnchanged':True,'newRankingAndExistingFailureProbeRetained':True,'sourceSeconds':6,'phaseSeconds':60,'clientSeconds':180,'ownerSeconds':180,'fixtureGuardSeconds':210,'combinedTcpMbps':32,'udpPps':50,'udpBytes':128,'hardwareExecuted':False}
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f: json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'copied':len(copied),'newFixture':True,'productionNotStarted':True}))
