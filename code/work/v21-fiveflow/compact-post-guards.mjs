// Factor identical postrouting identity guards into one dispatcher per exact flow/direction.
// Writers retain the original full guard. The three counters execute under that guard.
import assert from'node:assert/strict';
export function compactPostGuards(input){
 const plan=structuredClone(input),rows=plan.expected.nftables,groups=new Map(),chains=[],guards={};
 for(const x of rows){const r=x.rule;if(!r||r.chain!=='post')continue;const name=r.comment.slice(plan.owner.length+1),m=name.match(/^(tcp[234]?|udp)_post_(up|down)_(total|expected|unexpected)$/);if(!m)continue;const key=m[1]+'_post_'+m[2];if(!groups.has(key))groups.set(key,{});groups.get(key)[m[3]]=r;}
 assert.equal(groups.size,10);
 for(const[key,g]of groups){assert.deepEqual(Object.keys(g).sort(),['expected','total','unexpected']);const prefix=g.total.expr.slice(0,-1);assert.equal(prefix.length,20);assert.deepEqual(g.expected.expr.slice(0,-2),prefix);assert.deepEqual(g.unexpected.expr.slice(0,-2),prefix);assert.ok(g.total.expr.at(-1).counter);const name='g_'+key;
  guards[name]={dispatcherComment:plan.owner+':'+key+'_dispatch',slot:key.split('_')[0],direction:key.split('_')[2]};
  chains.push({chain:{family:'inet',table:plan.table,name}});
 }
 const output=[rows[0],...chains];
 for(const x of rows){if(x===rows[0])continue;const r=x.rule;if(!r||r.chain!=='post'){output.push(x);continue;}const name=r.comment.slice(plan.owner.length+1),m=name.match(/^(tcp[234]?|udp)_post_(up|down)_(total|expected|unexpected)$/);if(!m){output.push(x);continue;}if(m[3]!=='total')continue;
  const key=m[1]+'_post_'+m[2],g=groups.get(key),chain='g_'+key;
  output.push({rule:{...structuredClone(r),comment:guards[chain].dispatcherComment,expr:[...structuredClone(r.expr.slice(0,-1)),{jump:{target:chain}}]}});
  for(const kind of['total','expected','unexpected'])output.push({rule:{...structuredClone(g[kind]),chain,expr:structuredClone(g[kind].expr.slice(kind==='total'?-1:-2))}});
 }
 plan.expected.nftables=output;plan.guardedCounters=guards;
 // Expanding each generated counter through its sole dispatcher recovers every original rule.
 const expanded=output.filter(x=>x.rule||x.chain&&!guards[x.chain.name]||x.table).flatMap(x=>{const r=x.rule;if(!r)return[x];if(r.expr.at(-1)?.jump){const target=r.expr.at(-1).jump.target;return output.filter(y=>y.rule?.chain===target).map(y=>({rule:{...structuredClone(y.rule),chain:'post',expr:[...structuredClone(r.expr.slice(0,-1)),...structuredClone(y.rule.expr)]}}));}return guards[r.chain]?[]:[x];});
 assert.deepEqual(expanded,rows,'Factored NFT rule semantics differ');return plan;
}
