import fs from 'node:fs';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/v57-resident-bootstrap',read=p=>JSON.parse(fs.readFileSync(p,'utf8')),save=(n,v)=>fs.writeFileSync(root+'/'+n+'-'+Date.now()+'.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});
try{
 const model=read(read(root+'/entry-model-latest-private.json').receipt),runtime=model.modelRuntime,s=fs.readFileSync(runtime+'/read-controlled.mjs','utf8');
 const template=s.match(/const code=`([\s\S]*?)`;/)?.[1];assert.ok(template);const code=new Function('adapter','plan','config','routePorts','return `'+template+'`;')('return {}',{base:'unused',configSha256:'0'.repeat(64),workerSha256:'0'.repeat(64)},{clientAddress:'192.168.237.207',tcpServerAddress:'172.93.163.251'},[52000,52001,52002,52003]);
 assert.ok(!code.includes("gmatch('[^\n]+')"),'Interpolated Lua string contains an unescaped physical newline');
 const {naturalRotationPlan}=await import(pathToFileURL(process.cwd()+'/'+runtime+'/acquisition-plan.mjs'));
 const slots=['tcp','tcp2','tcp3','tcp4'],children=slots.map((slot,i)=>({slot,attempt:1,ownerPid:100+i,spawnedAt:'same'+i,connected:false}));
 const make=()=>({sourceAge:1,controlledClientPid:10,ownedTcpChildren:structuredClone(children),ownedTcpSlots:Object.fromEntries(slots.map((x,i)=>[x,52000+i])),ownedEstablishedTcpPorts:[52000,52001,52002,52003],flows:[],pairs:[],udp:[{decision:{class:'RT',budgetAdmitted:true},identity:{protocolNumber:17,wan:3,mark:3<<16}}],ownedTransportRoutes:[1,4,5,5].map((wan,i)=>({protocolNumber:6,wan,mark:wan<<16,original:{sport:52000+i,dport:22},localOwnedSocketVerified:true,nssAdmissionAllowed:false}))});
 const status=()=>({pid:10,elapsed:5,tcpChildren:structuredClone(children)});let checks=0;
 let f=make(),v=naturalRotationPlan(f,status());assert.deepEqual(v.commands,[{slot:'tcp4',attempt:2}]);assert.equal(f.pairs.length,0);checks++;
 f=make();f.ownedTransportRoutes=[];assert.equal(naturalRotationPlan(f,status()).unknown.length,4);checks++;
 f=make();f.ownedTcpChildren[3].ownerPid=999;assert.equal(naturalRotationPlan(f,status()).commands.length,0);checks++;
 f=make();f.ownedTcpChildren[3].attempt=2;assert.equal(naturalRotationPlan(f,status()).commands.length,0);checks++;
 f=make();f.sourceAge=6;assert.throws(()=>naturalRotationPlan(f,status()));checks++;
 f=make();f.ownedTransportRoutes[3].mark|=0x2000;assert.throws(()=>naturalRotationPlan(f,status()));checks++;
 f=make();f.ownedTransportRoutes.push({...f.ownedTransportRoutes[3]});assert.throws(()=>naturalRotationPlan(f,status()));checks++;
 f=make();f.ownedTransportRoutes[3].original.sport=53000;assert.equal(naturalRotationPlan(f,status()).commands.length,0);checks++;
 f=make();f.udp[0].decision.budgetAdmitted=false;assert.equal(naturalRotationPlan(f,status()).commands.length,0);checks++;
 f=make();const st=status();st.elapsed=30;assert.throws(()=>naturalRotationPlan(f,st));checks++;
 f=make();f.ownedTcpChildren[3].attempt=8;const end=status();end.tcpChildren[3].attempt=8;assert.throws(()=>naturalRotationPlan(f,end));checks++;
 let parser=code.slice(code.indexOf('local ports='),code.indexOf('print(j.stringify('));assert.ok(parser.startsWith('local ports='));
 parser=parser.replace(/local h=assert\(io\.popen\('[^']+'\)\);local ct=h:read\(65537\)or'';h:close\(\);assert\(#ct<=65536\);/,"local ct=T;assert(#ct<=65536);");assert.ok(!parser.includes('io.popen'));
 const row='ipv4 2 tcp 6 432000 ESTABLISHED src=192.168.237.207 dst=172.93.163.251 sport=52000 dport=22 src=172.93.163.251 dst=198.51.100.8 sport=22 dport=61000 [ASSURED] mark=327680 use=1 id=17';
 const cases=[{row,count:1},{row:row.replace('sport=52000','sport=53000'),count:0},{row:row.replace('mark=327680','mark=335872'),count:0},{row:row.replace('ESTABLISHED','SYN_SENT'),count:0},{row:row.replace('src=192.168.237.207','src=192.168.237.208'),count:0},{row:row.replace('dst=172.93.163.251','dst=172.93.163.250'),count:0},{row:row.replace('sport=22 dport=61000','sport=23 dport=61000'),count:0},{row:row.replace('mark=327680','mark=0'),count:0}];
 const ram="local j=require('luci.jsonc');assert(loadstring([========["+code+"]========]));local function parse(T)"+parser+"return routes end;local tests=assert(j.parse([===["+JSON.stringify(cases)+"]===]));for _,c in ipairs(tests)do local r=parse(c.row);assert(#r==c.count);if #r==1 then assert(r[1].wan==5 and r[1].original.sport==52000 and r[1].reply.dport==61000 and r[1].nssAdmissionAllowed==false)end end;assert(not pcall(parse,string.rep('X',65537)));print(j.stringify({passed=true,ramCases=9,fullLuaSyntaxPassed=true,routerWrites=false,trafficGenerated=false}))";
 const c=await connectRouter();let raw;try{const e=encode("lua - <<'V57_ROUTE_RAM'\n"+ram+"\nV57_ROUTE_RAM\n");raw=receipt(await c.run(e.command),e);}finally{c.close();}save('route-ram-raw-private',raw);assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.ok(result.passed);save('route-check',{passed:true,nodeCases:checks,...result,modelRuntime:runtime,sourceBindings:model.sourceBindings,nssAdmissionInferredFromRoute:false});console.log(JSON.stringify({passed:true,nodeCases:checks,...result}));
}catch(e){save('route-check-failure-private',{passed:false,error:String(e),stack:String(e.stack),productionExecuted:false});console.error(String(e));process.exitCode=1;}
