import fs from'node:fs';import assert from'node:assert/strict';import{persistentSsh}from'./persistent-ssh.mjs';
const load=JSON.parse(fs.readFileSync('work/v39-five-sim/load-latest-private.json'));assert.match(load.unit,/^v39-five-sim-[a-f0-9]{16}$/);const cp=JSON.parse(fs.readFileSync(load.dir+'/firewall-checkpoint-private.json'));
const guardian=fs.readFileSync('work/v39-five-sim/endpoint-firewall-guardian.py','utf8'),expected=fs.readFileSync('work/v39-five-sim/receiver.py','utf8')+'\n'+fs.readFileSync('work/v39-five-sim/server.py','utf8');
const code=guardian+`\nwith open('/proc/sys/kernel/random/boot_id') as f:assert f.read().strip()==${JSON.stringify(cp.boot)}
now=nft(['-j','list','ruleset'])
assert not [x for x in now['nftables'] if x.get('rule',{}).get('comment','').startswith('nss14-')]
assert hashlib.sha256(canonical(now).encode()).hexdigest()==${JSON.stringify(cp.canonicalSha256)}
unit=${JSON.stringify(load.unit+'.service')}
s=subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','ActiveState','-p','RuntimeMaxUSec'],text=True)
v=dict(x.split('=',1) for x in s.strip().splitlines());pid=int(v['MainPID'])
if pid:
 assert v['RuntimeMaxUSec']=='4min 10s'
 with open('/proc/'+str(pid)+'/cmdline','rb') as f:argv=f.read().decode().split('\\0')
 assert argv[2]=='-c' and argv[3]==${JSON.stringify(expected)}
 c=json.loads(argv[4]);assert c['mbps']==32 and c['seconds']==240 and c['tcpPort']==45817 and c['udpPort']==45818
 subprocess.run(['systemctl','stop',unit],check=True,timeout=10)
ports=subprocess.check_output(['ss','-H','-lntup'],text=True)
assert ':45817 ' not in ports and ':45818 ' not in ports
print(json.dumps({'passed':True,'ownedRulesRemaining':0,'baselineRestored':True,'exactOwnedEndpointClosed':True,'originalFailedTransportRetained':True}))
`;
const channel=persistentSsh();try{const r=await channel.exec('python3 -B -E -s -u -',code,{milliseconds:22000});fs.writeFileSync(load.dir+'/endpoint-retry-closure-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const v=JSON.parse(r.stdout);fs.writeFileSync(load.dir+'/endpoint-retry-closure.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(v));}finally{channel.close();}
