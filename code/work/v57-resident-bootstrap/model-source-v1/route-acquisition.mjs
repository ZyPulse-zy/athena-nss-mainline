import assert from 'node:assert/strict';
const once=(source,before,after)=>{assert.equal(source.split(before).length,2,before);return source.replace(before,after);};
export function patchNaturalAcquisition(source){
 source=once(source,'if(!current.connected||current.ownerPid!==captured.ownerPid','if(current.ownerPid!==captured.ownerPid');
 source=once(source,"if(flows.length!==1){unknown.push(slot);continue;}\n  const f=flows[0].identity;", "const routes=(frame.ownedTransportRoutes??[]).filter(r=>r.original.sport===port&&r.original.dport===22&&r.localOwnedSocketVerified===true);assert.ok(routes.length<=1,'Owned CT route ambiguous');\n  const f=flows.length===1&&current.connected?flows[0].identity:routes[0];if(!f){unknown.push(slot);continue;}");
 return source;
}
export function patchControlledReader(source){
 source="import{fileURLToPath}from'node:url';import path from'node:path';\n"+source;
 source=once(source,"const root=", "let readerConnection;export function closeControlledReader(){readerConnection?.close();readerConnection=undefined;}\nexport async function readControlled(){\nconst root=");
 source=once(source,"Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue|Where-Object{$ids -contains [int]$_.OwningProcess}","Get-NetTCPConnection -OwningProcess $ids -State Established -ErrorAction SilentlyContinue");
 const begin="const code=`local fs=";assert.equal(source.split(begin).length,2);
 source=source.replace(begin,"assert.match(config.clientAddress,/^192\\.168\\.237\\.207$/);assert.match(config.tcpServerAddress,/^172\\.93\\.163\\.251$/);const routePorts=pc.tcp.filter(x=>x.RemoteAddress===config.tcpServerAddress&&x.RemotePort===22).map(x=>x.LocalPort);assert.ok(routePorts.length<=4&&new Set(routePorts).size===routePorts.length&&routePorts.every(x=>Number.isInteger(x)&&x>0&&x<65536));\n"+begin);
 const code="local ports=assert(j.parse([===[${JSON.stringify(routePorts)}]===]));local allowed={};for _,p in ipairs(ports)do allowed[p]=true end;local h=assert(io.popen('conntrack -L -p tcp --orig-src 192.168.237.207 --orig-dst 172.93.163.251 -o extended,id 2>/dev/null'));local ct=h:read(65537)or'';h:close();assert(#ct<=65536);local routes={};for line in ct:gmatch('[^\\n]+')do local src,dst,sp,dp,rs,rd,rsp,rdp=line:match('tcp%s+6%s+%d+%s+ESTABLISHED%s+src=([^%s]+)%s+dst=([^%s]+)%s+sport=(%d+)%s+dport=(%d+).-src=([^%s]+)%s+dst=([^%s]+)%s+sport=(%d+)%s+dport=(%d+)');local mark=tonumber(line:match('mark=(%d+)'));local id=line:match('id=(%d+)');sp=tonumber(sp);dp=tonumber(dp);if src=='192.168.237.207'and dst=='172.93.163.251'and dp==22 and allowed[sp]and rs==dst and tonumber(rsp)==22 and rd and rdp and mark and id then local wan=math.floor(mark/65536)%256;if wan>=1 and wan<=5 and math.floor(mark/8192)%2==0 then routes[#routes+1]={protocolNumber=6,wan=wan,mark=mark,ctId=id,original={src=src,dst=dst,sport=sp,dport=dp},reply={src=rs,dst=rd,sport=tonumber(rsp),dport=tonumber(rdp)},localOwnedSocketVerified=true,nssAdmissionAllowed=false}end end end;";
 source=once(source,'print(j.stringify({producer=candidates.producer',code+'print(j.stringify({ownedTransportRoutes=routes,producer=candidates.producer');
 source=once(source,'const c=await connectRouter();','const c=readerConnection??=await connectRouter();');
 source=once(source,'console.log(JSON.stringify({controlledClientVerified:true,','return {controlledClientVerified:true,');
 source=once(source,'nssAdmissionAllowed:false}));}finally{c.close()}','nssAdmissionAllowed:false};}catch(e){closeControlledReader();throw e;}\n}\nif(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){try{console.log(JSON.stringify(await readControlled()));}finally{closeControlledReader();}}');
 return source;
}
export function patchMatcher(source){
 source="import{readControlled,closeControlledReader}from'./read-controlled.mjs';\n"+source;
 source=once(source,'while(performance.now()-began<35000){','try{while(performance.now()-began<35000){');
 source=once(source,"const p=spawnSync(process.execPath,[root+'/read-controlled.mjs'],{encoding:'utf8',windowsHide:true,timeout:15000});","let p;try{p={status:0,stdout:JSON.stringify(await readControlled())+'\\n',stderr:''};}catch(e){p={status:1,stdout:'',stderr:String(e)};}");
 source=once(source,"throw Error('Finite natural five-WAN matching expired without router stage');","throw Error('Finite natural five-WAN matching expired without router stage');}finally{closeControlledReader();}");
 return source;
}
