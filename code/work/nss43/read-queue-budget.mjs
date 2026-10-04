// Read current autorate queue settings. No configuration changes or NSS admission.
import fs from 'node:fs';import assert from 'node:assert/strict';
import {verifyPreparation} from './session-binding.mjs';
import {connectRouter} from '../nss20/connect-router.mjs';
verifyPreparation();const ctx=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json'));
const c=await connectRouter(),rows=[];
try{
 for(let wan=1;wan<=5;wan++){
  const name='rpifb'+wan,at=new Date().toISOString();
  const json=await c.run(ctx.base+'/group-runner 2 /sbin/tc -j qdisc show dev '+name);
  const text=await c.run(ctx.base+'/group-runner 2 /sbin/tc -s -d qdisc show dev '+name);
  assert.equal(json.code,0,json.stderr);assert.equal(text.code,0,text.stderr);
  const q=JSON.parse(json.stdout).filter(q=>q.kind==='cake'&&q.root);assert.equal(q.length,1);
  const match=text.stdout.match(/\bbandwidth\s+([\d.]+)([GMK]?bit)\b/);assert.ok(match);
  const multiplier={Gbit:1e9,Mbit:1e6,Kbit:1e3,bit:1}[match[2]];
  const textMbps=Number(match[1])*multiplier/1e6,jsonBytesPerSecond=q[0].options.bandwidth;
  // Rounded human text may differ slightly from JSON; permit 0.5% formatting error only.
  const unitsVerified=Math.abs(textMbps-jsonBytesPerSecond*8/1e6)<=Math.max(.001,textMbps*.005);
  rows.push({wan,observedAt:at,bandwidthMbps:textMbps,jsonBandwidthBytesPerSecond:jsonBytesPerSecond,
   unitsVerifiedByMatchingTextAndJson:unitsVerified,json:q,text:text.stdout});
 }
 const result={observedAt:new Date().toISOString(),readonly:true,routerWrites:false,
  captureAfterSteamProfile:true,autorateMayChangeBetweenReads:true,rows};
 fs.writeFileSync('work/nss43/current-queue-budget-private.json',JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({...result,rows:rows.map(({json,text,...row})=>row)}));
}finally{c.close()}
