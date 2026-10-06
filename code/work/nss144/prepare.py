from pathlib import Path
import hashlib,json
r=Path('work/nss144');r.mkdir(exist_ok=True)
def read(round,name):return (Path('work')/round/name).read_bytes()
def write(name,b):
    with (r/name).open('xb') as f:f.write(b)
names=['run.mjs','start-dallas.mjs','read-controlled.mjs','controlled-session.mjs','current-audit-diagnostic.mjs','close-endpoint.mjs','match-controlled.mjs','server.py','discover-peer.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1']
for name in names:
    b=read('nss128',name);s=b.replace(b'nss128',b'nss144').replace(b'NSS128',b'NSS144')
    assert s.replace(b'nss144',b'nss128').replace(b'NSS144',b'NSS128')==b
    if name=='start-dallas.mjs':
        assert s.count(b"config.bulkDirection='upload'")==1
        s=s.replace(b"config.bulkDirection='upload'",b"config.bulkDirection='download'")
    if name in ['controlled-session.mjs','current-audit-diagnostic.mjs']:
        imports=['declared-baseline.mjs','service-epoch.mjs','parse-ecm-any-wan.mjs','module-stage.mjs','uplink-tag-plan.mjs','compact-default-queues.mjs']
        for f in imports:s=s.replace(("'./"+f+"'").encode(),("'../nss140/"+f+"'").encode())
    if name=='controlled-session.mjs':
        s=s.replace(b"work/nss144/uplink-capacity-private.json",b"work/nss140/uplink-capacity-private.json")
    if name=='read-controlled.mjs':
        target=b"const adapter=fs.readFileSync('work/nss49/classifier.lua','utf8').split('\\n').filter(x=>!x.trimStart().startsWith('--')).join('\\n');"
        assert s.count(target)==1
        s=s.replace(target,b"const adapter=candidateAdapter(fs.readFileSync('work/nss49/classifier.lua','utf8')).source;")
        s=b"import{candidateAdapter}from'../nss143/candidate-adapter.mjs';\n"+s
    if name=='run.mjs':
        s=s.replace(b'actual-class to dual-leaf mapping / 20 second phases / downQoS30 / upQoS60 / offered32 / natural healthy WAN',b'current NSS140 factory / controlled download32 plus UDP / single healthy WAN')
        target=b"await run('work/nss144/controlled-session.mjs',['aba'],145)"
        assert s.count(target)==1
    write(name,s)
client=read('nss114','ssh-client.mjs')
client=client.replace(b'c.mbps===48',b'c.mbps===32')
old=b'const py="import os,time'
start=client.index(old);end=client.index(b'\nfunction connectTcp',start)
client=client[:start]+b"assert.equal(c.bulkDirection,'download');const py=fs.readFileSync(new URL('./download-server.py',import.meta.url),'utf8');"+client[end:]
client=client.replace(b"bulkTransport:'owned authenticated SSH TCP'",b"bulkTransport:'owned authenticated SSH TCP download',tcpMetric:'application received payload bytes',pacerDebtCatchupAllowed:false,maximumPacerCreditBytes:65536")
write('ssh-client.mjs',client)
health=read('nss142','health.mjs').replace(b"const root='work/nss142'",b"const root='work/nss144'")
write('health.mjs',health)
physical=read('nss142','read-final-physical.mjs').replace(b"const r='work/nss142'",b"const r='work/nss144'")
write('read-final-physical.mjs',physical)
receivers=read('nss142','verify-receivers.mjs').replace(b'nss142',b'nss144')
write('verify-receivers.mjs',receivers)
endpoints=read('nss142','verify-endpoints.mjs').replace(b"root='work/nss142'",b"root='work/nss144'")
write('verify-old-endpoints.mjs',endpoints)
print(json.dumps({'prepared':True,'direction':'download','offeredMbps':32,'udpPps':50,'unchangedNss140RouterPayload':True,'desktopOperated':False}))
