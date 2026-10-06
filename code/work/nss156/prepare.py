"""Owned raw upload fixture; no changes to classified native expiry/QoS/gate."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss155'
helpers=['start-dallas.mjs','match-controlled.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','failed-wan-owner.lua','declared-baseline.mjs','bounded-pacer.mjs','upload-ack.mjs','discover-peer.py','probe-peer.py','client-watchdog.ps1','endpoint-firewall-guardian.py','close-endpoint.mjs','crash-read.lua','module-stage.mjs','module-stage-guardian.lua','payload.mjs','fast-path.lua','close-control.mjs','exit-policy.mjs']
for n in helpers:
    p=r/n;assert not p.exists();s=(old/n).read_text(encoding='utf-8').replace('work/nss155','work/nss156').replace('nss155-','nss156-').replace('NSS155','NSS156')
    if n=='current-audit-diagnostic.mjs':s=s.replace('nss155\\/','nss156\\/')
    p.write_text(s,encoding='utf-8',newline='')
for a,b in [('epoch-driver-v3.mjs','epoch-driver.mjs'),('pilot-supervisor-v3.mjs','pilot-supervisor.mjs')]:
    p=r/b;assert not p.exists();s=(old/a).read_text(encoding='utf-8').replace('work/nss155','work/nss156').replace('NSS155','NSS156').replace('run3','run1').replace('session-binding-v3.mjs','session-binding.mjs')
    if a.startswith('pilot'):s=s.replace('epoch-driver-v3.mjs','epoch-driver.mjs').replace('frozen-qualified-inputs-v3','frozen-qualified-inputs').replace('entry-source-manifest-v3.json','entry-source-manifest.json').replace("['ssh']","['upload']")
    p.write_text(s,encoding='utf-8',newline='')
p=r/'start-dallas.mjs';s=p.read_text(encoding='utf-8')
s=s.replace('mbps:18,seconds:240','mbps:32,seconds:240').replace("const serverSource=fs.readFileSync(root+'/server.py','utf8');","const serverSource=fs.readFileSync(root+'/receiver.py','utf8')+'\\n'+fs.readFileSync(root+'/server.py','utf8');")
a=s.index("const sshBulk=process.argv[2]==='ssh';");b=s.index("const configPath=",a)
s=s[:a]+"assert.equal(process.argv[2],'upload');const rawUpload=true;config.mbps=32;config.bulkDirection='upload';config.tcpServerAddress=config.serverAddress;\n"+s[b:]
s=s.replace("root+(sshBulk?'/ssh-client.mjs':'/client.py')","root+'/raw-client.mjs'")
a=s.index('const launch=sshBulk?');b=s.index('\nconst p=spawnSync',a)
s=s[:a]+"const launch=ps.replace(\"$taskExe=(Get-Command python).Source\",'$taskExe='+literal(process.execPath)).replace(\"@('-u',\",\"@(\");"+s[b:]
s=s.replace("bulkTransport:sshBulk?'existing authenticated SSH TCP':'nonce authenticated raw TCP'","bulkTransport:'nonce authenticated raw TCP upload'")
assert 'sshBulk' not in s;p.write_text(s,encoding='utf-8',newline='')
print('Raw upload namespace created; fixed UDP peer and original FW/port/deadline budgets retained.')
