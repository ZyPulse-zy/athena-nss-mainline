import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss27/connect-router.mjs';
const root='work/nss108',h=x=>crypto.createHash('sha256').update(x).digest('hex');
const pidLua=`local u=assert(require('ubus').connect());local d=assert(u:call('service','list',{name='router-project-minieap'}));u:close()
local s=assert(d['router-project-minieap'],'Authenticator service missing');assert(type(s.instances)=='table','Invalid authenticator instances')
local n=assert(tonumber(arg[1]));assert(n%1==0 and n>=1 and n<=5)
local x=s.instances['wan'..n];assert(x==nil or type(x)=='table','Invalid authenticator instance')
local p=x and x.pid;assert(p==nil or type(p)=='number'and p%1==0 and p>1,'Invalid authenticator PID')
print(p or '')`;
const c=await connectRouter();try{
 const v=await c.run('cat /root/router-project/scripts/auth-recover.sh; printf "\\n__NSS108_MANIFEST__\\n"; cat /root/router-project/experiments/nss6-install-20260930/protected.sha256');assert.equal(v.code,0);
 const [source,manifest]=v.stdout.split('\n__NSS108_MANIFEST__\n');assert.ok(source&&manifest);
 for(const [name,bytes]of [['auth-before.sh',source],['protected-manifest-private.txt',manifest]]){const p=root+'/'+name;if(fs.existsSync(p))assert.equal(fs.readFileSync(p,'utf8'),bytes,'Live input changed since initial qualification');else fs.writeFileSync(p,bytes,{flag:'wx'});}
 const lines=source.split('\n').filter(x=>x.startsWith('pid=$(ubus call service list '));assert.equal(lines.length,1);const line=lines[0];assert.ok(line.includes('jsonfilter -e')&&line.includes('.instances.wan$n.pid'));assert.equal(source.split(line).length,2);
 const candidate=source.replace(line,"pid=$(/usr/bin/lua - \"$n\" <<'ATHENA_AUTH_PID'\n"+pidLua+"\nATHENA_AUTH_PID\n)");fs.writeFileSync(root+'/auth-candidate.sh',candidate,{flag:'wx'});
 const original="set -eu\npid=$(printf '%s' '{\"router-project-minieap\":{\"instances\":{\"wan4\":{\"running\":false}}}}' | jsonfilter -e '@[\"router-project-minieap\"].instances.wan4.pid')\nprintf 'EMPTY_BRANCH_REACHED:%s\\n' \"$pid\"\n";
 const old=await c.run("/bin/sh -s <<'NSS108_OLD_PID'\n"+original+"NSS108_OLD_PID\n");fs.writeFileSync(root+'/missing-pid-original-private.json',JSON.stringify(old,null,2)+'\n',{flag:'wx'});assert.equal(old.code,1);assert.ok(!old.stdout.includes('EMPTY_BRANCH_REACHED'));
 const fixtures=[['present',{instances:{wan4:{pid:123,running:true}}},true,'123'],['noPid',{instances:{wan4:{running:false}}},true,''],['noInstance',{instances:{}},true,''],['invalidPid',{instances:{wan4:{pid:'123'}}},false],['noInstances',{},false],['missingService',null,false]];
 const checks=[];for(const[name,value,ok,out]of fixtures){const script="local j=require('luci.jsonc');local value=j.parse([===["+JSON.stringify(value)+"]===]);package.loaded.ubus={connect=function()return{call=function()return value and{['router-project-minieap']=value}or{}end,close=function()end}end}\n"+pidLua;
 const r=await c.run("/usr/bin/lua - 4 <<'NSS108_PID_FIXTURE'\n"+script+"\nNSS108_PID_FIXTURE\n");assert.equal(r.code===0,ok,name);if(ok)assert.equal(r.stdout.trim(),out,name);checks.push({name,passed:true,simulated:true,accepted:ok});}
 const syntax=await c.run("/bin/sh -n -s <<'NSS108_AUTH_SYNTAX'\n"+candidate+"\nNSS108_AUTH_SYNTAX\n");assert.equal(syntax.code,0,syntax.stderr);
 const p={passed:true,checks,originalMissingPidExitCode:old.code,originalMissingPidBranchReached:false,sourceSha256:h(Buffer.from(source)),candidateSha256:h(Buffer.from(candidate)),targetFile:'/root/router-project/scripts/auth-recover.sh',onlyPidDiscoveryChanged:true,ubusErrorsStillFailClosed:true,protectedManifestIncludesTarget:manifest.includes('/root/router-project/scripts/auth-recover.sh'),targetShellSyntaxPassed:true,routerWrites:false};fs.writeFileSync(root+'/auth-qualification.json',JSON.stringify(p,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(p));
}finally{c.close()}
