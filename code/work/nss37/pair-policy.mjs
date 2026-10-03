// Select one observed application pair. Never rewrite marks, NAT or WAN affinity.
export function selectRealPair(candidates){
 const eligible=f=>Number.isInteger(f.identity.wan)&&f.identity.wan>=1&&f.identity.wan<=5&&Number.isInteger(f.identity.mark)&&f.identity.mark>0&&f.identity.mark<=0xffffffff&&Math.floor(f.identity.mark/65536)%256===f.identity.wan&&(f.identity.mark&0x2000)===0&&Number(f.identity.zone)===0&&f.identity.original.src==='192.168.237.207';
 const pairs=[];
 for(const g of candidates.game)for(const b of candidates.bulk){
  if(!eligible(g)||!eligible(b)||g.identity.protocolNumber!==17||b.identity.protocolNumber!==6||g.decision.class!=='RT'||g.decision.budgetAdmitted!==true||b.decision.class!=='BULK')continue;
  // The unchanged native gate currently requires identical full ct marks.
  if(g.identity.wan!==b.identity.wan||g.identity.mark!==b.identity.mark||g.identity.reply.dst!==b.identity.reply.dst)continue;
  pairs.push({g,b,score:(g.decision.pps??0)*1000000+(b.decision.rateKbps??0)});
 }
 pairs.sort((a,b)=>b.score-a.score);
 return pairs;
}
