from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss155'
def write(n,s):
    p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(old/'ssh-client.mjs').read_text(encoding='utf-8').replace('keepaliveInterval:2000','keepaliveInterval:0')
s=s.replace("if(x.udpSourcePort!==undefined&&x.udpSourcePort!==stats.udpSourcePort){rotate(x.udpSourcePort);return}","assert.equal(x.udpSourcePort??stats.udpSourcePort,c.udpSourcePort);")
s=s.replace('x.tcpSourcePort!==stats.tcpSourcePort)connectTcp','x.tcpSourcePort>stats.tcpSourcePort)connectTcp')
assert 'keepaliveInterval:0' in s and 'keepaliveInterval:2000' not in s;write('ssh-client-v6.mjs',s);write('upload-server.py',(old/'upload-server.py').read_text(encoding='utf-8'))
s=(r/'start-dallas-v3.mjs').read_text(encoding='utf-8');o=(old/'start-dallas.mjs').read_text(encoding='utf-8');a=o.index('if(sshBulk){')+len('if(sshBulk){');b=o.index('\nconst configPath=',a);config=o[a:b];assert config.endswith('}');config=config[:-1]
a=s.index("assert.equal(process.argv[2],'upload');const rawUpload=true;");b=s.index('\nconst configPath=',a)
s=s[:a]+"assert.equal(process.argv[2],'upload');"+config+s[b:];s=s.replace("root+'/raw-client-v2.mjs'","root+'/ssh-client-v6.mjs'").replace("bulkTransport:'nonce authenticated raw TCP upload'","bulkTransport:'owned SSH upload with fixture-only keepalive disabled'")
write('start-dallas-v6.mjs',s)
write('epoch-driver-v6.mjs',(r/'epoch-driver-v5.mjs').read_text(encoding='utf-8').replace('./session-binding-v5.mjs','./session-binding-v6.mjs').replace('work/nss156/run5/','work/nss156/run6/'))
s=(r/'pilot-supervisor-v5.mjs').read_text(encoding='utf-8').replace('./session-binding-v5.mjs','./session-binding-v6.mjs').replace('./epoch-driver-v5.mjs','./epoch-driver-v6.mjs').replace("out=root+'/run5'","out=root+'/run6'").replace("root+'/start-dallas-v3.mjs'","root+'/start-dallas-v6.mjs'").replace('frozen-qualified-inputs-v5','frozen-qualified-inputs-v6').replace('entry-source-manifest-v5.json','entry-source-manifest-v6.json');write('pilot-supervisor-v6.mjs',s)
s=(r/'session-binding-v5.mjs').read_text(encoding='utf-8').replace("from './session-binding-v4.mjs'","from './session-binding-v5.mjs'").replace('entry-qualified-v5.json','entry-qualified-v6.json');write('session-binding-v6.mjs',s)
print('Existing keyed and pinned SSH fixture: per-process keepalive disabled; original receiver/PC deadlines and eight-port budget retained.')
