import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {root} from './build-classifier.mjs';import {verifyDeployment} from './deployment-binding.mjs';import {waitReady} from './wait-ready-candidate.mjs';import {executeLua,luaLiteral} from './lua-local.mjs';
const current=verifyDeployment(),label='local-cache-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');let command;
await waitReady({async run(s){command=s;return{code:0,stderr:'',stdout:JSON.stringify({passed:true,alignment:{producer:'model',selectedSequence:2}})};}},current.deployment,label);
const unquoted=command.replaceAll("'\\''","'"),from="<<'NSS41_WAIT_FULL'\n";assert.ok(unquoted.includes(from));
const lua=unquoted.split(from)[1].split('\nNSS41_WAIT_FULL\n')[0];
const marker=' -- Compact publication is cheap to parse. Inode reuse must not freeze a query.\n do';assert.equal(lua.split(marker).length,2);
const old=lua.replace(marker,' if not cached or st.dev~=cached.dev or st.ino~=cached.ino then');
const spec={base:current.deployment.base,configHash:current.deployment.configHash,generation:current.config.generation,boot:current.config.adoptionBoot};
function replay(source,expected){return String.raw`
local clock=0.4;local P=${luaLiteral(spec)};local original=io.open;local lastClass
local function sample()
 local seq=math.floor((clock-0.1)/3)+1;local start=(seq-1)*3
 return{publication='before-software-baseline',status='running',dataHealthy=true,nssPermit=false,configSha256=P.configHash,generation=P.generation,boot=P.boot,pid=123,start='99',producer='model',atUptime=start+0.1,
 snapshot={flows={},admissionProjection={version=1,scope='bulk-and-admitted-rt',sourceSequence=seq,candidateFlowCount=0,completeInputFlowCount=0},provenance={sequence=seq,version=1,method='conntrack-cli',rawStatus=0,exitCode=0,boot=P.boot,startedAtUptime=start,finishedAtUptime=start+0.05}}}
end
local function body(path)
 if path=='/proc/uptime'then return tostring(clock)..' 0' end
 if path:match('^/sys/kernel/debug/ecm/')then return path:match('_stop$')and '1' or '0'end
 if path=='/root/router-project/game-classifier-generation'then return P.base..' '..P.configHash..'\n'end
 if path=='/proc/sys/kernel/random/boot_id'then return P.boot..'\n'end
 if path=='/tmp/router-project-game-classifier/classification.json'then lastClass=sample();return 'classification'end
 if path=='/tmp/router-project-game-classifier/guardian.json'then return 'guardian'end
 if path=='/proc/123/stat'then local a={'S','1'};for i=3,20 do a[i]='0'end;a[20]='99';return '123 (lua) '..table.concat(a,' ')end
 if path=='/proc/123/cmdline'then return table.concat({'/usr/bin/lua',P.base..'/worker.lua','watch',P.base,P.configHash},'\0')..'\0'end
 error('Unexpected replay path '..path)
end
io.open=function(path)return{read=function()return body(path)end,close=function()return true end}end
package.preload['nixio']=function()return{nanosleep=function()clock=clock+0.1 end}end
package.preload['nixio.fs']=function()return{lstat=function(path)if path=='/root/router-project/active-transaction'or path:match('/stopped$')then return nil end;return{type='reg',uid=0,gid=0,nlink=1,dev=1,ino=7}end}end
package.preload['luci.jsonc']=function()return{parse=function(text)
 if text=='classification'then return lastClass end
 if text=='guardian'then return{healthy=true,producer='model',configSha256=P.configHash,atUptime=clock}end
 return P
end,stringify=function(result)assert(result.passed==${expected});if result.passed then assert(result.alignment.selectedSequence==2 and result.alignment.sourceAge<2)end;return 'REPLAY_OK' end}end
assert(loadstring(${luaLiteral(source)}))();io.open=original
`;}
for(const [name,source,expected]of [['old-inode-cache',old,false],['fresh-publication',lua,true]]){const r=executeLua(replay(source,expected),name);assert.equal(r.code,0,r.stderr);assert.ok(r.stdout.includes('REPLAY_OK'));}
const out={passed:true,checks:2,actualLua51Executed:true,oldInodeReuseSchedulingRefusalReproduced:true,currentSnapshotParsedEachPoll:true,freshSourceUnderTwoSecondsRetained:true,routerAccess:false};
fs.writeFileSync(root+'/wait-cache-tests-latest.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
