import fs from'node:fs';import assert from'node:assert/strict';import{persistentSsh}from'./persistent-ssh.mjs';
const load=JSON.parse(fs.readFileSync('work/v27-raw/load-latest-private.json'));assert.match(load.unit,/^v27-raw-[a-f0-9]{16}$/);
const code=`import json,subprocess
n=json.loads(subprocess.check_output(['nft','-j','list','ruleset'],text=True))
r=[x['rule'] for x in n['nftables'] if x.get('rule',{}).get('comment','').startswith('nss14-')]
print(json.dumps({'ownedRuleCounters':[{'protocol':'tcp' if x['comment'].endswith('-tcp') else 'udp','counters':[y['counter'] for y in x['expr'] if 'counter' in y]} for x in r]}))
print(subprocess.check_output(['ss','-H','-nt','sport','=',':45817'],text=True))
print(subprocess.check_output(['journalctl','-u',${JSON.stringify(load.unit+'.service')},'--no-pager','-n','8','-o','cat'],text=True))
`;
const c=persistentSsh();try{const r=await c.exec('python3 -B -E -s -u -',code,{milliseconds:12000});fs.writeFileSync(load.dir+'/firstbyte-diagnostic-v2-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const lines=r.stdout.trim().split(/\r?\n/);console.log(JSON.stringify({readonly:true,ownedCounters:JSON.parse(lines[0]),tcpSocketRows:lines.filter(x=>/^(ESTAB|SYN-RECV|CLOSE-WAIT|TIME-WAIT)/.test(x)).length,endpointReadySeen:r.stdout.includes('CONTROLLED_ENDPOINT_READY'),unhandledExceptionSeen:r.stdout.includes('Traceback'),productionNssWrites:false}));}finally{c.close()}
