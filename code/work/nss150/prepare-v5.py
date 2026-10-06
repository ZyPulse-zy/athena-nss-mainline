from pathlib import Path
import json,hashlib
r=Path('work/nss150');p=json.loads((r/'entry-qualified-v4.json').read_text(encoding='utf-8'))
for n in ['run-v4.mjs','controlled-session-v4.mjs','current-audit-diagnostic-v4.mjs']:
    b=(r/n).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sourceManifest'][(r/n).as_posix()]
    s=b.replace(b'session-binding-v4.mjs',b'session-binding-v5.mjs')
    if n=='run-v4.mjs':
        s=s.replace(b'frozen-qualified-inputs-v4',b'frozen-qualified-inputs-v5').replace(b'entry-source-manifest-v4.json',b'entry-source-manifest-v5.json')
        s=s.replace(b"output=root+'/run-v4'",b"output=root+'/run-v5'").replace(b'controlled-session-v4.mjs',b'controlled-session-v5.mjs').replace(b'current-audit-diagnostic-v4.mjs',b'current-audit-diagnostic-v5.mjs')
        s=s.replace(b'automatic-v4-preflight',b'automatic-v5-preflight').replace(b"root+'/start-dallas.mjs'",b"root+'/start-dallas-v5.mjs'")
    if n=='controlled-session-v4.mjs':
        s=s.replace(b'current-audit-diagnostic-v4.mjs',b'current-audit-diagnostic-v5.mjs').replace(b'work/nss150/run-v4/continuity-private.json',b'work/nss150/run-v5/continuity-private.json')
    with (r/n.replace('-v4.mjs','-v5.mjs')).open('xb') as f:f.write(s)
b=(r/'start-dallas.mjs').read_bytes();p0=json.loads((r/'entry-qualified.json').read_text(encoding='utf-8'))
assert hashlib.sha256(b).hexdigest()==p0['sourceManifest'][(r/'start-dallas.mjs').as_posix()]
a=b"const unit='nss150-'+session;"
z=b"const priorLoad=JSON.parse(fs.readFileSync('work/nss149/load-latest-private.json'));const priorConfig=JSON.parse(fs.readFileSync(priorLoad.dir+'/client-config-private.json'));const priorRuntime=JSON.parse(fs.readFileSync('work/nss149/automatic-history-private.json'));assert.equal(priorRuntime.history.length,1);assert.equal(priorRuntime.history[0].closedAndRestored,true);assert.equal(priorRuntime.history[0].selected.udp.wan,1);assert.equal(priorConfig.udpPort,45818);assert.equal(priorConfig.serverAddress,'172.93.163.251');const seededUdpPort=priorConfig.udpSourcePort;assert.ok(Number.isInteger(seededUdpPort)&&seededUdpPort>=59000&&seededUdpPort<59800);const portCheck=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command','@{count=@(Get-NetUDPEndpoint -LocalPort '+seededUdpPort+' -ErrorAction SilentlyContinue).Count}|ConvertTo-Json -Compress'],{encoding:'utf8',windowsHide:true,timeout:8000});save('prior-owned-port-preflight-private',{code:portCheck.status,stdout:portCheck.stdout,stderr:portCheck.stderr});assert.equal(portCheck.status,0);assert.equal(JSON.parse(portCheck.stdout.replace(/^\\uFEFF/,'')).count,0);save('prior-owned-port-seed-private',{originalProof:priorRuntime,priorConfig,linuxPbrStillSelectsWan:true,udpNotRotatedDuringMatching:true});\nconst unit='nss150-'+session;"
assert b.count(a)==1;b=b.replace(a,z)
a=b'udpSourcePort:59000+crypto.randomInt(800)';assert b.count(a)==1;b=b.replace(a,b'udpSourcePort:seededUdpPort')
with (r/'start-dallas-v5.mjs').open('xb') as f:f.write(b)
with (r/'load-v4-reference-private.json').open('xb') as f:f.write((r/'load-latest-private.json').read_bytes())
print(json.dumps({'prepared':True,'ownedUdpPortSeedOnly':True,'noPbrNatOrFirewallScopeExpansion':True,'oldWan5FailureRetained':True,'factoryAndPolicyUnchanged':True,'routerWrites':False}))
