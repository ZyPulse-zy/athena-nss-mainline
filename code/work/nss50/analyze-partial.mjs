// Actual software-only samples. Missing NSS phases are never manufactured.
import fs from 'node:fs';import assert from 'node:assert/strict';
const dirs=['real-matched-aba-20261004083435-f36f1fcc','real-matched-aba-20261004083901-c4b7888d'];
const cpu=s=>s.cpu.split('\n')[0].trim().split(/\s+/).slice(1,9).map(Number);
const soft=s=>s.softnet.trim().split('\n').map(l=>l.trim().split(/\s+/).slice(0,3).map(v=>parseInt(v,16)));
const results=[];
for(const name of dirs){
 const dir='work/nss50/'+name,r=JSON.parse(fs.readFileSync(dir+'/last-record-private.json')),selection=JSON.parse(fs.readFileSync(dir+'/selected-private.json')),p=r.phases[0];assert.ok(p.completed&&p.name==='A'&&r.phases.length===1&&!r.newNssPermit);
 const s=r.samples.slice(p.sampleStart-1,p.sampleEnd);assert.ok(s.length===11&&s.every(s=>s.phase==='A'&&Object.values(s.counts).every(x=>x===0)&&s.stop4===1&&s.stop6===1));
 const a=s[0],b=s.at(-1),seconds=b.uptime-a.uptime;const d=cpu(b).map((n,i)=>n-cpu(a)[i]);assert.ok(d.every(x=>x>=0));const total=d.reduce((a,b)=>a+b,0);
 const sa=soft(a),sb=soft(b);const softChanges=[0,0,0];for(let i=0;i<sa.length;i++)for(let k=0;k<3;k++){const n=sb[i][k]-sa[i][k];softChanges[k]+=n>=0?n:n+2**32;}
 const interfaces={};for(const dev of['lan4','rpwan'+selection.tcp.wan]){const x=a.interfaces[dev],y=b.interfaces[dev];interfaces[dev]={};for(const k of['rx_bytes','tx_bytes','rx_packets','tx_packets','rx_dropped','tx_dropped']){const n=y[k]-x[k];assert.ok(Number.isSafeInteger(n)&&n>=0);interfaces[dev][k]=n;}Object.assign(interfaces[dev],{rxMbps:(y.rx_bytes-x.rx_bytes)*8/seconds/1e6,txMbps:(y.tx_bytes-x.tx_bytes)*8/seconds/1e6,rxPps:(y.rx_packets-x.rx_packets)/seconds,txPps:(y.tx_packets-x.tx_packets)/seconds});}
 results.push({case:name,wan:selection.tcp.wan,phase:'A',seconds,samples:s.length,busyPercent:(total-d[3]-d[4])*100/total,softirqPercent:d[6]*100/total,timeSqueeze:softChanges[2],softnetDrop:softChanges[1],interfaces,softwareForwarding:true,commonNssLan4QueueTreeStaged:true,ecmPermitOpened:false,phasesBAndA2Missing:true,cpuBenefitConclusion:false,gameBenefitConclusion:false,rollbackPassed:['tagsRemoved','qosRestored','qosModuleUnloaded','wanRestored','mwan3Restored','stateNodeRemoved'].every(k=>r[k]===true)});
}
const out={readonlyOfflineAnalysis:true,cases:results,noBetweenCaseCausalComparison:true,missingDataNeverZero:true};fs.writeFileSync('work/nss50/partial-a-sanitized.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
