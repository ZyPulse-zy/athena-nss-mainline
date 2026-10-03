// Correct the historical WAN5-only report parser in a separate postprocessing copy.
// Frozen controller inputs and native experiment record stay unchanged.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const dir='work/nss41/real-matched-aba-20261003165708-9086b676',root='work/nss41';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');const original=fs.readFileSync('work/nss25/parse-ecm.mjs','utf8');
assert.equal(original.split("v==='rpwan5'").length-1,1);assert.equal(original.split('wanAffinity:5').length-1,1);
const candidate=original.replace("v==='rpwan5'","v==='rpwan'+f.wan").replace('wanAffinity:5','wanAffinity:f.wan');
fs.writeFileSync(root+'/parse-ecm-any-wan.mjs',candidate);const {validateAcceleratedState}=await import(pathToFileURL(process.cwd()+'/'+root+'/parse-ecm-any-wan.mjs'));
const record=JSON.parse(fs.readFileSync(dir+'/last-record-private.json')),selected=JSON.parse(fs.readFileSync(dir+'/selected-private.json'));
const proof=validateAcceleratedState(record.acceleratedState,selected);assert.equal(proof.proof.tcp.wanAffinity,1);assert.equal(proof.proof.udp.wanAffinity,1);
const cases=[{case:'actual frozen WAN1 TCP+UDP state',passed:true}];
for(const [name,change] of [['wrong selected WAN',()=>{const x=structuredClone(selected);x.tcp.wan=5;return[record.acceleratedState,x]}],['wrong full CT mark',()=>{const x=structuredClone(selected);x.tcp.mark^=0x100;return[record.acceleratedState,x]}],['wrong expected NAT port',()=>{const x=structuredClone(selected);x.udp.reply.dport++;return[record.acceleratedState,x]}],['missing private WAN layer',()=>[record.acceleratedState.replaceAll('=rpwan1','=rpwan9'),selected]],['wrong expected RT tag',()=>[record.acceleratedState.replaceAll('=2399535104','=2399469568'),selected]],['wrong accelerated mode',()=>[record.acceleratedState.replaceAll('nss_v4.ported.accel_mode=2','nss_v4.ported.accel_mode=1'),selected]]]){const[raw,expected]=change();assert.throws(()=>validateAcceleratedState(raw,expected),name);cases.push({case:name,passed:true});}
fs.writeFileSync(dir+'/actual-accelerated-state-revalidated.json',JSON.stringify(proof,null,2)+'\n');const out={passed:true,checks:cases.length,cases,originalParserSha256:hash(original),candidateParserSha256:hash(candidate),frozenStateSha256:hash(record.acceleratedState),nativeRecordUnchanged:true,nativeExperimentNotRerun:true,scope:'Postprocessing actual frozen hardware state; hardcoded WAN5 corrected to selected WAN. Mutated copies verify rejection. Does not retroactively change failed controller status or qualify high-load CPU/game performance.',routerWrites:false};fs.writeFileSync(root+'/actual-state-parser-qualified.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({passed:true,checks:cases.length,actualAcceleratedFlows:proof.connectionCount,wan:1,tcp:{...proof.proof.tcp},udp:{...proof.proof.udp}}));
