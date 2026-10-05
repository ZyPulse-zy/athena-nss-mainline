import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const bytes=fs.readFileSync('work/nss89/fast-path.lua'),helper=fs.readFileSync('work/nss89/tag-counter-audit.lua','utf8').replaceAll('\r','');assert.ok(bytes.toString().replaceAll('\r','').startsWith('local M={}\n'+helper));
const cases=[];function add(name,patch,pass,prior=false,pending=false,need=false){cases.push({name,patch,pass,prior,pending,need})}
add('equal positive',[],true);add('live skew requests one bracket',[['tcp_post_down_expected','packets',11],['tcp_post_down_expected','bytes',2500]],true,false,false,true);
add('bounded bracket allows progress',[],true,true);add('byte-only skew requests bracket',[['tcp_post_up_expected','bytes',1001]],true,false,false,true);
for(const k of ['tcp_post_up','tcp_post_down','udp_post_up','udp_post_down']){
 add(k+' wrong packet',[[k+'_unexpected','packets',1],[k+'_unexpected','bytes',40]],false);
 add(k+' wrong byte',[[k+'_unexpected','bytes',1]],false);
 add(k+' missing',[[k+'_total','missing',true]],false);
 add(k+' regression',[[k+'_total','packets',9],[k+'_total','bytes',900]],false,true);
}
add('negative', [['tcp_post_up_total','packets',-1]],false);add('fractional',[['tcp_post_up_total','bytes',0.5]],false);add('string',[['tcp_post_up_total','packets','10']],false);
add('neighbor packet',[['udp_post_neighbor_nonzero','packets',1],['udp_post_neighbor_nonzero','bytes',156]],false);add('neighbor byte',[['udp_post_neighbor_nonzero','bytes',1]],false);
add('no overlap',[['tcp_post_up_expected','packets',1],['tcp_post_up_expected','bytes',100]],false,true);
const zero=[['udp_post_down_total','packets',0],['udp_post_down_total','bytes',0],['udp_post_down_expected','packets',0],['udp_post_down_expected','bytes',0]];
add('initial zero remains pending',zero,true,false,true);add('later zero never authorizes',zero,false,false,false);
const record=JSON.parse(fs.readFileSync('work/nss88/controlled-matched-aba-20261005101439-546037e0/last-record-private.json'));
function extract(raw){const c={};for(const x of raw.nftables??[])if(x.rule)for(const e of x.rule.expr??[])if(e.counter)c[x.rule.comment.split(':').at(-1)]=e.counter;return c}
const observed={prior:extract(record.initialTagsFirst),current:extract(record.initialTags)};
const code=`local j=require('luci.jsonc');local M={};${helper}
local cases=j.parse([====[${JSON.stringify(cases)}]====]);local base={};for _,k in ipairs({'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down'})do base[k..'_total']={packets=10,bytes=1000};base[k..'_expected']={packets=10,bytes=1000};base[k..'_unexpected']={packets=0,bytes=0}end;base.udp_post_neighbor_nonzero={packets=0,bytes=0}
for _,v in ipairs(cases)do local c=j.parse(j.stringify(base));for _,e in ipairs(v.patch)do if e[2]=='missing'then c[e[1]]=nil else c[e[1]][e[2]]=e[3]end end;local ok,r=pcall(M.tagCounterAudit,c,v.pending,v.prior and base or nil);assert(ok==v.pass,v.name);if ok then assert(r.needsSecond==v.need,v.name..' bracket')end end
local observed=j.parse([====[${JSON.stringify(observed)}]====]);local a=M.tagCounterAudit(observed.current,true,observed.prior);assert(a.pending and a.bracketValidated and not a.needsSecond);local ok=pcall(M.tagCounterAudit,observed.current,false,observed.prior);assert(not ok,'Recorded absent UDP down must not authorize')
print(j.stringify({passed=true,cases=#cases+2,recordedNonAtomicSnapshotsCovered=true,recordedMissingDownlinkStillRefused=true,nssAdmissionAllowed=false}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS89_COUNTER_CONTRACT'\n"+code+"\nNSS89_COUNTER_CONTRACT\n");const raw=receipt(await c.run(e.command),e);fs.writeFileSync('work/nss89/getter-raw-private.json',JSON.stringify(raw,null,2));assert.equal(raw.code,0,raw.stderr);const p=JSON.parse(raw.stdout);p.sourceSha256=crypto.createHash('sha256').update(bytes).digest('hex');fs.writeFileSync('work/nss89/getter-qualified.json',JSON.stringify(p,null,2)+'\n');const manifest={};for(const f of fs.readdirSync('work/nss89'))if(/\.(mjs|py|ps1|lua)$/.test(f))manifest['work/nss89/'+f]=crypto.createHash('sha256').update(fs.readFileSync('work/nss89/'+f)).digest('hex');assert.deepEqual(fs.readFileSync('work/nss89/qos-physical.lua'),fs.readFileSync('work/nss88/qos-physical.lua'));const q={passed:true,onlyCounterObservationChanged:true,qosGroupMbps:60,tcpOfferedMbps:52,fastSourceSha256:p.sourceSha256,oneOwnedRereadMaximum:true,wrongTagPacketAndByteZeroRequired:true,fullPolicyValidationUnchanged:true,sourceAndNativeLifetimeBoundsUnchanged:true,sourceManifest:manifest};fs.writeFileSync('work/nss89/entry-qualified.json',JSON.stringify(q,null,2)+'\n');console.log(JSON.stringify(p));}finally{c.close()}
