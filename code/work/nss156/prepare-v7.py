from pathlib import Path
r=Path(__file__).resolve().parent
def write(n,s):
    p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'start-dallas-v6.mjs').read_text(encoding='utf-8').replace("root+'/ssh-client-v6.mjs'","root+'/cohort-client.mjs'");write('start-dallas-v7.mjs',s)
s=(r/'read-controlled.mjs').read_text(encoding='utf-8')
s=s.replace('f.identity.original.sport===status.tcpSourcePort','status.tcpCandidatePorts.includes(f.identity.original.sport)')
anchor='assert.ok(status.tcpSourcePort>=config.tcpSourcePort';assert anchor in s
s=s.replace(anchor,"assert.ok(Array.isArray(status.tcpCandidatePorts)&&status.tcpCandidatePorts.length<=4);for(const port of status.tcpCandidatePorts)assert.ok(Number.isInteger(port)&&port>=config.tcpSourcePort&&port<config.tcpSourcePort+8);"+anchor)
s=s.replace('const out={...native,','const ownedEstablishedTcpPorts=pc.tcp.filter(e=>e.RemoteAddress===config.tcpServerAddress&&e.RemotePort===config.tcpPort&&e.LocalPort>=config.tcpSourcePort&&e.LocalPort<config.tcpSourcePort+8).map(e=>e.LocalPort);const out={...native,ownedEstablishedTcpPorts,')
write('read-controlled-v7.mjs',s)
s=(r/'epoch-driver-v6.mjs').read_text(encoding='utf-8').replace('./session-binding-v6.mjs','./session-binding-v7.mjs').replace('work/nss156/run6/','work/nss156/run7/').replace("observationRoot+'/read-controlled.mjs'","observationRoot+'/read-controlled-v7.mjs'");write('epoch-driver-v7.mjs',s)
s=(r/'pilot-supervisor-v6.mjs').read_text(encoding='utf-8').replace('./session-binding-v6.mjs','./session-binding-v7.mjs').replace('./epoch-driver-v6.mjs','./epoch-driver-v7.mjs').replace("out=root+'/run6'","out=root+'/run7'").replace("root+'/start-dallas-v6.mjs'","root+'/start-dallas-v7.mjs'").replace("root+'/match-controlled.mjs'","root+'/match-cohort.mjs'").replace('frozen-qualified-inputs-v6','frozen-qualified-inputs-v7').replace('entry-source-manifest-v6.json','entry-source-manifest-v7.json')
s=s.replace("selected=read(root,'controlled-candidates-private').pairs[0]","selected=read(root,'controlled-candidates-private').pairs[0]")
s=s.replace("const next=status.tcpSourcePort+1;assert.ok(next<config.tcpSourcePort+8);", "assert.equal(status.preparationCohort,0);")
s=s.replace("{session:config.session,closeTcp:false,tcpSourcePort:next}","{session:config.session,prepareSuccessor:true}");write('pilot-supervisor-v7.mjs',s)
s=(r/'session-binding-v6.mjs').read_text(encoding='utf-8').replace("from './session-binding-v5.mjs'","from './session-binding-v6.mjs'").replace('entry-qualified-v6.json','entry-qualified-v7.json');write('session-binding-v7.mjs',s)
print('Four software-only probes share one global 32Mbps pacer. Other sockets close before NSS; four ports reserved for fresh successor.')
