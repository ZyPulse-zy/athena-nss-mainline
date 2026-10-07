import assert from 'node:assert/strict';
export function nextUdpCandidate({attempt,peers,clientLaunched,firewallLaunched,used,draw}){
 assert.ok(Number.isInteger(attempt)&&attempt>=1&&attempt<=3);
 assert.ok(Array.isArray(peers)&&peers.length===0&&clientLaunched===false&&firewallLaunched===false,'UDP tuple is immutable after authentication or launch');
 assert.ok(Array.isArray(used)&&used.length===attempt-1&&new Set(used).size===used.length);
 if(attempt===1)return undefined;
 const available=Array.from({length:800},(_,i)=>59000+i).filter(p=>!used.includes(p));
 const index=draw(available.length);assert.ok(Number.isInteger(index)&&index>=0&&index<available.length);return available[index];
}
export function patchUdpDiscovery(source){
 source="import{nextUdpCandidate}from'../resident-dev-20261007/udp-discovery.mjs';\n"+source;
 const before='for(let attempt=1;attempt<=3;attempt++){';assert.equal(source.split(before).length,2);
 source=source.replace(before,`const usedUdpPorts=[];
for(let attempt=1;attempt<=3;attempt++){
 const next=nextUdpCandidate({attempt,peers,clientLaunched:false,firewallLaunched:false,used:usedUdpPorts,draw:n=>crypto.randomInt(n)});
 if(next!==undefined){const check=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command','@{count=@(Get-NetUDPEndpoint -LocalPort '+next+' -ErrorAction SilentlyContinue).Count}|ConvertTo-Json -Compress'],{encoding:'utf8',windowsHide:true,timeout:8000});save('udp-candidate-port-'+attempt+'-private',{code:check.status,stdout:check.stdout,stderr:check.stderr});assert.equal(check.status,0);assert.equal(JSON.parse(check.stdout.replace(/^\\uFEFF/,'')).count,0);config.udpSourcePort=next;}
 usedUdpPorts.push(config.udpSourcePort);assert.equal(new Set(usedUdpPorts).size,usedUdpPorts.length);save('udp-discovery-input-'+attempt+'-private',{config,attempt,clientLaunched:false,firewallLaunched:false,routerPolicyWrites:false});save('client-config-private',config);`);
 source=source.replace('oneFreshInitialOwnedUdpPort:true','initialUdpCandidatePrepared:true,maximumDiscoveryCandidates:3,udpChangesOnlyBeforeClientAndFirewall:true');
 assert.ok(source.includes('attempt<=3')&&source.includes("assert.equal(peers.length,1,'Authenticated actual public peer absent after bounded same-port discovery')"));
 return source;
}
