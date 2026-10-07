import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';import{persistentSsh}from'./persistent-ssh.mjs';
const root='work/v42-counter-window',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),cp=JSON.parse(fs.readFileSync(load.dir+'/firewall-checkpoint-private.json'));
assert.match(load.unit,/^v42-counter-window-[a-f0-9]{16}$/);assert.ok(Date.now()>fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+252000,'Original endpoint maximum lifetime not elapsed');
fs.writeFileSync(root+'/one-endpoint-readonly-recheck.json',JSON.stringify({oneAttemptOnly:true,readonly:true,originalClosureTransportFailurePreserved:true})+'\n',{flag:'wx'});
const dir=root+'/endpoint-readonly-recheck-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
const guardian=fs.readFileSync(root+'/endpoint-firewall-guardian.py','utf8');
const code=guardian+`\nwith open('/proc/sys/kernel/random/boot_id') as f:assert f.read().strip()==${JSON.stringify(cp.boot)}
now=nft(['-j','list','ruleset'])
assert not [x for x in now['nftables'] if x.get('rule',{}).get('comment','').startswith('nss14-')]
assert hashlib.sha256(canonical(now).encode()).hexdigest()==${JSON.stringify(cp.canonicalSha256)}
unit=${JSON.stringify(load.unit+'.service')}
s=subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','ActiveState','-p','RuntimeMaxUSec'],text=True)
v=dict(x.split('=',1) for x in s.strip().splitlines());assert int(v['MainPID'])==0
assert v['ActiveState'] in ('inactive','failed')
ports=subprocess.check_output(['ss','-H','-lntup'],text=True)
assert ':45817 ' not in ports and ':45818 ' not in ports
print(json.dumps({'passed':True,'readonly':True,'ownedRulesRemaining':0,'baselineRestored':True,'exactOwnedEndpointClosed':True,'originalClosureTransportFailurePreserved':True,'independentEndpointDeadlineElapsed':True}))
`;
const c=persistentSsh();try{const r=await c.exec('python3 -B -E -s -u -',code,{milliseconds:22000});fs.writeFileSync(dir+'/raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);fs.writeFileSync(dir+'/summary.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});fs.writeFileSync(root+'/endpoint-readonly-recheck-pointer.json',JSON.stringify({directory:dir})+'\n',{flag:'wx'});console.log(JSON.stringify(out));}catch(e){fs.writeFileSync(dir+'/failure-private.json',JSON.stringify({error:String(e),readonly:true})+'\n',{flag:'wx'});throw e}finally{c.close()}
