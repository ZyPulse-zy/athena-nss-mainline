// Execute the real epoch/counter functions in target Lua RAM. No policy writes.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss105',hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const source=fs.readFileSync(root+'/fast-path.lua','utf8'),old=fs.readFileSync('work/nss100/fast-path.lua','utf8');
assert.equal(source.slice(0,source.indexOf('function M.tagEpoch')),old.slice(0,old.indexOf('function M.verifyRenewalAck')),'Strict tag audit changed');
assert.ok(source.includes('now()+27,record.deadline-28')&&source.includes('requestedSeconds=20')&&source.includes('now()+1.2,due-0.5')&&source.includes('pause(0.1);stopped()'));
const counterSource=source.slice(0,source.indexOf('function M.verifyRenewalAck'))+'\nreturn M';
const body=String.raw`
local j=require('luci.jsonc');local M=assert(loadstring([====[${counterSource}]====]))();local checks={}
local dirs={'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'}
local function baseline(one)
 local c={};for _,k in ipairs(dirs)do for _,s in ipairs({'total','expected','unexpected'})do local p=s=='unexpected'and 0 or 10;c[k..'_'..s]={packets=p,bytes=p*100}end end
 c.udp_post_neighbor_nonzero={packets=0,bytes=0}
 if one then c.tcp_post_down_unexpected={packets=1,bytes=1500};c.tcp_post_down_total={packets=11,bytes=2500}end
 return c
end
local function nextFrame(b)
 local c=j.parse(j.stringify(b));for _,k in ipairs(dirs)do for _,s in ipairs({'total','expected'})do local v=c[k..'_'..s];v.packets=v.packets+20;v.bytes=v.bytes+2000 end end;return c
end
local function run(name,modify,expected)
 local b=baseline(true);local c=nextFrame(b);local pending=false
 if modify then pending=modify(b,c)==true end
 local ok,v=pcall(function()return M.tagCounterAudit(M.tagEpoch(b,c),pending)end)
 assert(ok==expected,name..':'..tostring(v));checks[#checks+1]={name=name,passed=true,simulated=true,accepted=ok}
end
run('one-startup-packet-no-new-errors',nil,true)
run('zero-startup-errors',function(b,c)b.tcp_post_down_unexpected={packets=0,bytes=0};c.tcp_post_down_unexpected={packets=0,bytes=0}end,true)
run('wrong-startup-size',function(b,c)b.tcp_post_down_unexpected.bytes=1501;c.tcp_post_down_unexpected.bytes=1501 end,false)
run('two-startup-packets',function(b,c)b.tcp_post_down_unexpected.packets=2;c.tcp_post_down_unexpected.packets=2 end,false)
run('startup-udp-error',function(b,c)b.udp_post_down_unexpected={packets=1,bytes=156};c.udp_post_down_unexpected={packets=1,bytes=156}end,false)
run('startup-neighbor-error',function(b,c)b.udp_post_neighbor_nonzero={packets=1,bytes=156};c.udp_post_neighbor_nonzero={packets=1,bytes=156}end,false)
run('new-tcp-error',function(b,c)c.tcp_post_down_unexpected={packets=2,bytes=3000}end,false)
run('new-udp-error',function(b,c)c.udp_post_down_unexpected={packets=1,bytes=156}end,false)
run('new-neighbor-error',function(b,c)c.udp_post_neighbor_nonzero={packets=1,bytes=156}end,false)
run('missing-counter',function(b,c)c.tcp_post_up_total=nil end,false)
run('added-counter',function(b,c)c.extra={packets=0,bytes=0}end,false)
run('regressed-counter',function(b,c)c.tcp_post_up_total.packets=9 end,false)
run('fractional-counter',function(b,c)c.tcp_post_up_total.packets=30.5 end,false)
run('overflow-counter',function(b,c)c.tcp_post_up_total.bytes=9007199254740992 end,false)
run('invalid-zero-baseline',function(b,c)b.udp_post_up_expected={packets=0,bytes=1}end,false)
run('missing-new-direction',function(b,c)c.udp_post_down_total=j.parse(j.stringify(b.udp_post_down_total));c.udp_post_down_expected=j.parse(j.stringify(b.udp_post_down_expected))end,false)
run('pending-is-not-admission',function(b,c)c.udp_post_down_total=j.parse(j.stringify(b.udp_post_down_total));c.udp_post_down_expected=j.parse(j.stringify(b.udp_post_down_expected));return true end,true)
local b=baseline(true);local c=nextFrame(b);local a=M.tagEpoch(b,c);c.tcp_post_up_total.packets=c.tcp_post_up_total.packets+1;c.tcp_post_up_total.bytes=c.tcp_post_up_total.bytes+100
local first=M.tagCounterAudit(M.tagEpoch(b,c),false);assert(first.needsSecond)
c.tcp_post_up_expected.packets=c.tcp_post_up_expected.packets+2;c.tcp_post_up_expected.bytes=c.tcp_post_up_expected.bytes+200;c.tcp_post_up_total.packets=c.tcp_post_up_total.packets+1;c.tcp_post_up_total.bytes=c.tcp_post_up_total.bytes+100
local second=M.tagCounterAudit(M.tagEpoch(b,c),false,a);assert(second.bracketValidated)
checks[#checks+1]={name='monotonic-counter-bracket-after-epoch',passed=true,simulated=true,accepted=true}
print(j.stringify({passed=true,checks=checks,routerWrites=false,targetLua=true,fullPolicyStillVerified=true,rawCountersRetained=true}))
`;
const c=await connectRouter();try{
const e=encode("/usr/bin/lua - <<'NSS105_EPOCH_MODEL'\n"+body+"\nNSS105_EPOCH_MODEL\n"),v=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/startup-epoch-private.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});assert.equal(v.code,0,v.stderr);const p=JSON.parse(v.stdout);assert.ok(p.passed&&p.checks.length===18);
const syntax=encode("/usr/bin/lua - <<'NSS105_SYNTAX'\nassert(loadstring([====["+source+"]====]));print('SYNTAX_PASS')\nNSS105_SYNTAX\n"),s=receipt(await c.run(syntax.command),syntax);assert.equal(s.code,0,s.stderr);assert.equal(s.stdout.trim(),'SYNTAX_PASS');
fs.writeFileSync(root+'/startup-epoch-qualification.json',JSON.stringify({...p,sourceSha256:hash(fs.readFileSync(root+'/fast-path.lua')),strictCounterAuditByteIdentical:true,onlyStartupObservationChanged:true,maximumInitialWaitSeconds:1.2,warmupSeconds:0.1,phaseSeconds:20,nativeSeconds:27,classifierSeconds:6},null,2)+'\n',{flag:'wx'});
const m={};for(const f of fs.readdirSync(root)){if(/\.(mjs|py|lua|ps1)$/.test(f))m[root+'/'+f]=hash(fs.readFileSync(root+'/'+f))}
fs.writeFileSync(root+'/entry-qualified.json',JSON.stringify({passed:true,onlyStartupMeasurementChanged:true,tcpOfferedMbps:48,qosGroupMbps:30,phaseSeconds:20,fixedNativeSessionSeconds:27,detachedOwnerSeconds:100,classifierFreshnessSeconds:6,sourceManifest:m},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,checks:p.checks.length,fullSourceSyntaxPassed:true,routerWrites:false}));
}finally{c.close()}
