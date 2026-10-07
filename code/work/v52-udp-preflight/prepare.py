"""Retain compact SSH and compare real UDP echo carriers before the full client."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent;old=w/'work/v51-compact-entry'
assert not (root/'preparation.json').exists()
hashes={}
for name in ['entry.mjs','materialize.mjs','fixture-startup.mjs','platform-preflight.mjs','ssh-phase.mjs','ssh-options.mjs','recheck-endpoint-readonly.mjs']:
    blob=(old/name).read_bytes();hashes['work/v51-compact-entry/'+name]=hashlib.sha256(blob).hexdigest()
    s=blob.decode().replace('v51-compact-entry','v52-udp-preflight').replace('v51-run','v52-run')
    if name=='entry.mjs':
        needle="const loadPath=runtimeRoot+'/load-latest-private.json';let endpointPassed=!fs.existsSync(loadPath);"
        assert s.count(needle)==1
        s=s.replace(needle,"const loadPath=runtimeRoot+'/load-latest-private.json',setupPath=runtimeRoot+'/endpoint-setup-private.json';let endpointPassed=!fs.existsSync(loadPath)&&!fs.existsSync(setupPath);\n  if(!fs.existsSync(loadPath)&&fs.existsSync(setupPath)){const setup=read(setupPath),due=fs.statSync(setup.dir+'/server-deadline-private.json').mtimeMs+252000;while(Date.now()<=due)await new Promise(r=>setTimeout(r,Math.min(1000,due-Date.now()+1)));endpointPassed=(await command('partial-endpoint-closure',runtimeRoot+'/recheck-partial-endpoint.mjs',[],30))===0;}" )
        needle="else if(!fs.existsSync(loadPath))clientCode=0;"
        assert s.count(needle)==1
        s=s.replace(needle,"else if(!fs.existsSync(loadPath)&&fs.existsSync(setupPath)&&fs.existsSync(runtimeRoot+'/closure-pointer.json'))clientCode=await command('no-client-closure',runtimeRoot+'/capture-no-client-closure.ps1',[],30,true);\n  else if(!fs.existsSync(loadPath)&&!fs.existsSync(setupPath))clientCode=0;")
    if name=='materialize.mjs':
        needle="if(name==='pilot-supervisor.mjs'){"
        assert s.count(needle)==1
        s=s.replace(needle,"if(name==='start-dallas.mjs'){let s=bytes.toString();const needle=\"const literal=x=>\";assert.equal(s.split(needle).length,2);s=s.replace(needle,\"fs.writeFileSync(root+'/endpoint-setup-private.json',JSON.stringify({dir,unit,clientLaunchNotRequested:true})+'\\\\n',{flag:'wx'});const udpProof=spawnSync(process.execPath,[root+'/check-udp-path.mjs',dir],{encoding:'utf8',windowsHide:true,timeout:13000,maxBuffer:65536});save('udp-path-command-private',{code:udpProof.status,stdout:udpProof.stdout,stderr:udpProof.stderr});assert.equal(udpProof.status,0,'UDP echo preflight refused before client; original output retained');\\n\"+needle);bytes=Buffer.from(s);}\n  "+needle)
        needle="const binding=`import fs from'node:fs';"
        assert s.count(needle)==1
        extra="for(const name of ['udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1']){const source=fs.readFileSync(entryRoot+'/'+name,'utf8').replaceAll('__RUNTIME__',runtimeRoot);fs.writeFileSync(runtimeRoot+'/'+name,source,{flag:'wx'});generatedHashes[runtimeRoot+'/'+name]=hash(Buffer.from(source));}\n "
        s=s.replace(needle,extra+needle)
        needle="'ssh-options.mjs','recheck-endpoint-readonly.mjs'"
        assert s.count(needle)==1
        s=s.replace(needle,needle+",'udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1'")
    with (root/name).open('x',encoding='utf8',newline='') as f:f.write(s)
proof={'passed':True,'priorSourcesUnchanged':hashes,'preClientActualUdpEchoProbesAdded':True,'preClientPartialEndpointClosureAdded':True,
       'dataPlaneClassificationQosAndOriginalLifetimeLimitsUnchanged':True}
with (root/'preparation.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
print(json.dumps({'passed':True,'priorSources':len(hashes)}))
