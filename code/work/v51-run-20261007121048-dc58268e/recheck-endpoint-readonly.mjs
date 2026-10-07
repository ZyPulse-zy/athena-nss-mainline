import fs from 'node:fs';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {compactSshOptions} from '../v51-compact-entry/ssh-options.mjs';

const root='work/v51-run-20261007121048-dc58268e',read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
assert.match(root,/^work\/v51-run-\d{14}-[a-f0-9]{8}$/);
const load=read(root+'/load-latest-private.json');assert.ok(load.dir.startsWith(root+'/load-'));
const settings=read(load.dir+'/firewall-settings-private.json'),launch=read(load.dir+'/launch-receipt.json');
assert.match(launch.unit,/^v51-run-\d{14}-[a-f0-9]{8}-[a-f0-9]{16}$/);
assert.ok(Date.now()>=fs.statSync(load.dir+'/launch-receipt.json').mtimeMs+252000,'Original server deadline must have elapsed');
const code=fs.readFileSync(root+'/endpoint-firewall-guardian.py','utf8')+`\nc=${JSON.stringify(settings)}\nwith open('/proc/sys/kernel/random/boot_id') as f:boot=f.read().strip()\nassert boot==c['boot']\nrules=nft(['-j','list','ruleset'])\nowned=[x['rule'] for x in rules['nftables'] if x.get('rule',{}).get('comment','').startswith('nss14-'+c['owner']+'-')]\nassert not owned\nassert hashlib.sha256(canonical(rules).encode()).hexdigest()==c['baselineCanonicalSha256']\np=subprocess.run(['ss','-H','-lntup'],capture_output=True,text=True,timeout=5)\nassert p.returncode==0 and not any(':45817 ' in x or ':45818 ' in x for x in p.stdout.splitlines())\nq=subprocess.run(['systemctl','show',${JSON.stringify(launch.unit)},'-p','MainPID','-p','ActiveState'],capture_output=True,text=True,timeout=5)\nassert 'MainPID=0' in q.stdout and 'ActiveState=active' not in q.stdout\nprint(json.dumps({'passed':True,'readonly':True,'ownedRulesRemaining':0,'baselineRestored':True,'exactOwnedEndpointClosed':True,'independentNaturalDeadlinesKept':True}))\n`;
assert.ok(Buffer.byteLength(code)<=65536);
const p=spawnSync('ssh',[...compactSshOptions,'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
  '-o','ConnectTimeout=8','-o','ServerAliveInterval=3','-o','ServerAliveCountMax=1','sub2api-dallas','python3 -B -E -s -u -'],
  {input:code,encoding:'utf8',windowsHide:true,timeout:20000,maxBuffer:65536});
fs.writeFileSync(load.dir+'/endpoint-readonly-recheck-raw-private.json',JSON.stringify({code:p.status,stdout:p.stdout,stderr:p.stderr,error:p.error?.code??null},null,2)+'\n',{flag:'wx'});
assert.equal(p.status,0,'Readonly recovery recheck failed; raw output retained');
const result=JSON.parse(p.stdout);assert.ok(result.passed&&result.readonly);
fs.writeFileSync(load.dir+'/endpoint-readonly-recheck.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
