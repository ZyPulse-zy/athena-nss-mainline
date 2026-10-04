// Read-only diagnostics. A later snapshot cannot reconstruct the rejected frame.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const label=process.argv[2];assert.match(label,/^[a-z0-9-]+$/);
const caseDir=process.argv[3];assert.match(caseDir,/^work\/nss49\/real-matched-aba-\d+-[a-f0-9]+$/);
const selected=JSON.parse(fs.readFileSync(caseDir+'/selected-private.json'));
const pc=JSON.parse(fs.readFileSync('work/nss49/pc-app-endpoints-private.json'));
const ids=new Map(pc.processes.map(p=>[p.pid,p.name]));
const ports=new Set(pc.udp.filter(e=>ids.get(e.OwningProcess)==='cs2').map(e=>e.LocalPort));
const path='work/nss50/selected-'+label+'-private.json';assert.ok(!fs.existsSync(path));
const code="local j=require('luci.jsonc');local f=assert(io.open('/tmp/router-project-game-classifier/classification.json'));local raw=f:read(4194305);f:close();assert(#raw<=4194304);local u=assert(io.open('/proc/uptime'));local t=tonumber(u:read(128):match('^[%d.]+'));u:close();print(j.stringify({uptime=t,publication=assert(j.parse(raw)),readonly=true,nssAdmissionAllowed=false}))";
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS50_CLASS_READONLY'\n"+code+"\nNSS50_CLASS_READONLY\n");
 const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);
 const data=JSON.parse(r.stdout);fs.writeFileSync(path,JSON.stringify(data,null,2)+'\n',{flag:'wx'});
 const flows=data.publication.snapshot.flows;
 const simple=f=>f?{protocol:f.identity.protocolNumber,wan:f.identity.wan,class:f.decision.class,reason:f.decision.reason,budgetAdmitted:f.decision.budgetAdmitted,rateKbps:f.decision.rateKbps,pps:f.decision.pps,blockedUntil:f.decision.blockedUntil}:null;
 const out={readonly:true,retrospectiveCauseProven:false,sourceAge:data.uptime-data.publication.snapshot.provenance.startedAtUptime,configSha256:data.publication.configSha256,slots:Object.fromEntries(['tcp','udp'].map(slot=>[slot,{keyPresent:flows.some(f=>f.key===selected[slot].classifierKey),current:simple(flows.find(f=>f.key===selected[slot].classifierKey))}])),currentCs2SocketMatching:flows.filter(f=>f.identity.protocolNumber===17&&ports.has(f.identity.original.sport)).map(simple),nssAdmissionAllowed:false};
 fs.writeFileSync('work/nss50/selected-'+label+'-sanitized.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
}finally{c.close()}
