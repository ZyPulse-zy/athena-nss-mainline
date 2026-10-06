import fs from'node:fs';import assert from'node:assert/strict';import{persistentSsh}from'../v27-raw/persistent-ssh.mjs';
const root=process.argv[2];assert.match(root,/^work\/morning-20261007\/run-\d{14}-[a-f0-9]{8}$/);assert.ok(fs.statSync(root).isDirectory());const folders=['v12','v13-two','v14-duration','v15-qos','v16-three','v17-cap','v18-borrow','v19-borrow','v20-five','v21-fiveflow','v22-fiveflow','v23-fiveflow','v24-fiveflow','v27-raw'],units=new Set();
for(const name of folders){const d='work/'+name;if(!fs.existsSync(d))continue;for(const n of fs.readdirSync(d)){const p=d+'/'+n;if(!n.startsWith('load-')||!fs.statSync(p).isDirectory()||!fs.existsSync(p+'/launch-receipt.json'))continue;const r=JSON.parse(fs.readFileSync(p+'/launch-receipt.json'));if(r.unit){assert.match(r.unit,/^[a-zA-Z0-9-]+$/);units.add(r.unit+'.service');}}}
assert.ok(units.size>=10);const load=JSON.parse(fs.readFileSync('work/v27-raw/load-latest-private.json')),cp=JSON.parse(fs.readFileSync(load.dir+'/firewall-checkpoint-private.json')),guardian=fs.readFileSync('work/v27-raw/endpoint-firewall-guardian.py','utf8');
const code=guardian+`\nwith open('/proc/sys/kernel/random/boot_id') as f:assert f.read().strip()==${JSON.stringify(cp.boot)}
now=nft(['-j','list','ruleset']);assert not [x for x in now['nftables'] if x.get('rule',{}).get('comment','').startswith('nss14-')]
assert hashlib.sha256(canonical(now).encode()).hexdigest()==${JSON.stringify(cp.canonicalSha256)}
for unit in ${JSON.stringify([...units])}:
 p=subprocess.run(['systemctl','show',unit,'-p','MainPID','-p','ActiveState','-p','LoadState'],capture_output=True,text=True,timeout=3)
 v=dict(s.split('=',1) for s in p.stdout.strip().splitlines());assert int(v.get('MainPID','-1'))==0 and v.get('ActiveState') in ['inactive','failed']
ports=subprocess.check_output(['ss','-H','-lntup'],text=True);assert ':45817 ' not in ports and ':45818 ' not in ports
print(json.dumps({'passed':True,'readonly':True,'knownOwnedUnitsChecked':${units.size},'ownedUnitsInactiveMainPidZero':True,'temporaryFirewallRulesRemaining':0,'canonicalFirewallBaselineMatched':True,'tcpAndUdpEndpointPortsClosed':True,'remoteWrites':False}))
`;
const c=persistentSsh();try{const r=await c.exec('python3 -B -E -s -u -',code,{milliseconds:20000});fs.writeFileSync(root+'/endpoint-audit-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const out={...JSON.parse(r.stdout),observedAt:new Date().toISOString()};fs.writeFileSync(root+'/endpoint-audit.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));}finally{c.close()}
