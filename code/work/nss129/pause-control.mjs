import fs from'node:fs';import assert from'node:assert/strict';
import{connectRouter}from'../nss27/connect-router.mjs';
import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';

export function setApplicationPause(load,paused,proofDir){
 assert.equal(typeof paused,'boolean');const config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'));
 const status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
 assert.equal(status.pid,load.clientPid);assert.equal(status.session,config.session);assert.ok(status.tcpConnected&&Date.now()/1000-status.at<2);
 const path=load.dir+'/control.json';const before=fs.existsSync(path)?JSON.parse(fs.readFileSync(path)):{session:config.session};assert.equal(before.session,config.session);
 const next={...before,pauseTcp:paused};fs.writeFileSync(path+'.new',JSON.stringify(next));fs.renameSync(path+'.new',path);
 const r={at:new Date().toISOString(),paused,applicationPayloadOnly:true,sameTcpSocketRequested:true,udpUnchanged:true,clientPid:status.pid,tcpSourcePort:status.tcpSourcePort,udpSourcePort:status.udpSourcePort,before,after:next,clientIndependentDeadlineSeconds:210};
 fs.writeFileSync(proofDir+'/'+(paused?'application-pause':'application-resume')+'-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});return r;
}
export async function pauseAfterOwnedAcceleration(load,context){
 const c=await connectRouter(),due=performance.now()+45000,reads=[];
 const code=`local f=require('nixio.fs');local j=require('luci.jsonc');local function r(p)local h=assert(io.open(p));local s=h:read(8193);h:close();assert(#s<=8192);return s:gsub('%s+$','')end;local m='/sys/module/rp_ecm_gate_lab_ct/parameters/';local x={at=tonumber(r('/proc/uptime'):match('^[%d.]+')),stop=tonumber(r('/sys/kernel/debug/ecm/front_end_ipv4_stop')),count=tonumber(r('/sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count'))};if f.lstat(m)then x.hash=r(m..'frozen_record_sha256');x.epoch=r(m..'epoch_refresh');x.tcp=r(m..'tcp_permit');x.udp=r(m..'game_permit')end;print(j.stringify(x))`;
 try{
  while(performance.now()<due){const e=encode("lua - <<'NSS129_OWNED_PAUSE_READ'\n"+code+"\nNSS129_OWNED_PAUSE_READ\n");const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const v=JSON.parse(raw.stdout);reads.push(v);
   if(v.count===2&&v.stop===0){assert.equal(v.hash,context.plan.frozenHash);assert.equal(v.tcp,'Y');assert.equal(v.udp,'Y');const r=setApplicationPause(load,true,context.dir);fs.writeFileSync(context.dir+'/pause-trigger-private.json',JSON.stringify({passed:true,readOnlyRouterWatcher:true,readings:reads,trigger:v,application:r},null,2)+'\n',{flag:'wx'});return r;}
   assert.ok(v.count===0||v.count===1,'Unexpected pretrigger ECM count');await new Promise(r=>setTimeout(r,250));
  }throw Error('Owned accelerated pair never reached pause trigger');
 }finally{c.close()}
}
