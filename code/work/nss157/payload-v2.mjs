import fs from 'node:fs';import assert from 'node:assert/strict';import {packLua} from '../nss149/pack-lua.mjs';
// Factor shared rule metadata and comment prefix. Restore exact JSON semantics
// before native use; no classifier, lease, tag, or firewall rule is omitted.
export function buildPayload(input,{qos,phase,classifier,tags,normalizer}){
 const pool=[],refs=[],skeleton=structuredClone(input.tagPlan),rules=skeleton.expected.nftables.filter(x=>x.rule).map(x=>x.rule);assert.ok(rules.length);
 const meta={};for(const [k,v] of Object.entries(rules[0]))if(k!=='expr'&&k!=='comment'&&rules.every(r=>JSON.stringify(r[k])===JSON.stringify(v)))meta[k]=v;
 for(const r of rules)for(const k of Object.keys(meta))delete r[k];
 let prefix=rules[0].comment;assert.equal(typeof prefix,'string');for(const r of rules){assert.equal(typeof r.comment,'string');while(!r.comment.startsWith(prefix))prefix=prefix.slice(0,-1)}
 for(const r of rules)r.comment=r.comment.slice(prefix.length);
 for(const[i,x]of skeleton.expected.nftables.entries())if(x.rule){const ids=x.rule.expr.map(e=>{const key=JSON.stringify(e);let n=pool.findIndex(p=>JSON.stringify(p)===key);if(n<0){n=pool.length;pool.push(e)}return n+1});delete x.rule.expr;refs.push([i+1,ids])}
 const packed={s:skeleton,p:pool,r:refs,m:meta,x:prefix},unpacked=structuredClone(skeleton);
 for(const r of unpacked.expected.nftables)if(r.rule){for(const[k,v]of Object.entries(meta)){assert.ok(!(k in r.rule));r.rule[k]=structuredClone(v)}r.rule.comment=prefix+r.rule.comment}
 for(const r of refs)unpacked.expected.nftables[r[0]-1].rule.expr=r[1].map(i=>structuredClone(pool[i-1]));assert.deepEqual(unpacked,input.tagPlan);
 const data=JSON.stringify(packed);assert.ok(!data.includes(']====]'));
 const tagSource="local j=require('luci.jsonc');local p=assert(j.parse([====["+data+"]====]));for _,x in ipairs(p.s.expected.nftables)do if x.rule then for k,v in pairs(p.m)do assert(x.rule[k]==nil);x.rule[k]=v end;x.rule.comment=p.x..x.rule.comment end end;for _,r in ipairs(p.r)do local e={};for _,i in ipairs(r[2])do e[#e+1]=assert(j.parse(j.stringify(p.p[i])))end;p.s.expected.nftables[r[1]].rule.expr=e end;return p.s";
 const source='local qos=(function()\n'+packLua(qos)+'\nend)();local phase=(function()\n'+packLua(phase)+'\nend)();local classifier=(function()\n'+packLua(classifier)+'\nend)();local tags=(function()\n'+packLua(tags)+'\nend)();local normalizer=(function()\n'+packLua(normalizer)+'\nend)();local tagPlan=(function()\n'+tagSource+'\nend)();local fast=(function()\n'+packLua(fs.readFileSync('work/nss157/fast-path.lua','utf8'))+'\nend)();local wan=(function()\n'+packLua(fs.readFileSync('work/nss49/wan-scope.lua','utf8'))+'\nend)();local state=(function()\n'+packLua(fs.readFileSync('work/nss49/state-node.lua','utf8'))+'\nend)();return{qos=qos,phase=phase,classifier=classifier,tags=tags,normalizer=normalizer,tagPlan=tagPlan,fast=fast,wan=wan,state=state}\n';
 return {stagedCode:source,tagSource};
}
