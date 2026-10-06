import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync}from'node:child_process';
const dir=process.argv[2],m=dir?.match(/^work\/v13-two\/load-\d{14}-([a-f0-9]{16})$/);assert.ok(m);
assert.ok(!fs.existsSync(dir+'/firewall-receipt-private.json'),'Use full recovery after firewall writes');
const checkpoint=JSON.parse(fs.readFileSync(dir+'/server-checkpoint-private.json'));
const boot=checkpoint.before.trim().split(/\r?\n/).at(-1);assert.match(boot,/^[a-f0-9-]{36}$/);
const expected=fs.readFileSync('work/v13-two/receiver.py','utf8')+'\n'+fs.readFileSync('work/v13-two/server.py','utf8');
const code=`import json,subprocess,os
unit=${JSON.stringify('v13-two-'+m[1])}
expected=${JSON.stringify(expected)}
with open('/proc/sys/kernel/random/boot_id') as f:assert f.read().strip()==${JSON.stringify(boot)}
state=subprocess.check_output(['systemctl','show',unit+'.service','-p','MainPID','-p','ActiveState','-p','RuntimeMaxUSec'],text=True)
values=dict(x.split('=',1) for x in state.strip().splitlines())
pid=int(values['MainPID'])
if pid:
 assert values['RuntimeMaxUSec']=='4min 10s'
 with open('/proc/'+str(pid)+'/cmdline','rb') as f:argv=f.read().decode().split('\\0')
 assert argv[2]=='-c' and argv[3]==expected
 config=json.loads(argv[4]);assert config['mbps']==32 and config['seconds']==240 and config['tcpPort']==45817 and config['udpPort']==45818
 subprocess.run(['systemctl','stop',unit+'.service'],check=True,timeout=10)
rules=json.loads(subprocess.check_output(['nft','-j','list','ruleset'],text=True))
assert not [x for x in rules['nftables'] if x.get('rule',{}).get('comment','').startswith('nss14-')]
listeners=subprocess.check_output(['ss','-H','-lntup'],text=True)
assert ':45817 ' not in listeners and ':45818 ' not in listeners
print(json.dumps({'passed':True,'partialOsEndpointClosedOrExpired':True,'exactSourceAndFixedDataCheckedIfRunning':True,'noExperimentFirewallRules':True}))
`;
const r=spawnSync('ssh',['-o','BatchMode=yes','-o','ConnectTimeout=6','-o','ServerAliveInterval=3','-o','ServerAliveCountMax=1','sub2api-dallas','python3 -B -E -s -u -'],{input:code,encoding:'utf8',windowsHide:true,timeout:22000});
fs.writeFileSync(dir+'/unverified-endpoint-closure-raw-private.json',JSON.stringify({code:r.status,stdout:r.stdout,stderr:r.stderr,error:r.error?String(r.error):null},null,2)+'\n',{flag:'wx'});
assert.equal(r.status,0,'Endpoint cleanup failed; original result retained');console.log(r.stdout.trim());
