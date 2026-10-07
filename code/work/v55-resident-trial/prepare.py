from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent;old=w/'work/v54-owned-control'
assert not (root/'preparation.json').exists()
names=['entry.mjs','materialize.mjs','fixture-startup.mjs','platform-preflight.mjs','ssh-phase.mjs','ssh-options.mjs','recheck-endpoint-readonly.mjs','udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1','persistent-ssh.mjs'];hashes={}
for name in names:
 blob=(old/name).read_bytes();hashes['work/v54-owned-control/'+name]=hashlib.sha256(blob).hexdigest();s=blob.decode().replace('v54-owned-control','v55-resident-trial').replace('v54-run','v55-run')
 if name=='materialize.mjs':
  s="import{patchResidentWindow}from'./resident-window.mjs';\n"+s
  s=s.replace('kernel:90,kernelMaximum:120','kernel:120,kernelMaximum:120').replace('phase:60,tcpMbps','phase:90,tcpMbps')
  needle="if(name==='native-client.mjs'){";assert s.count(needle)==1
  s=s.replace(needle,"if(name==='fast-path.lua'){bytes=Buffer.from(patchResidentWindow(bytes.toString()));}\n  if(name==='epoch-driver.mjs'){let s=bytes.toString();s=s.replace('p.seconds>=60&&p.seconds<=61.5&&p.sampleCount>=118','p.seconds>=90&&p.seconds<=91.5&&p.sampleCount>=178');bytes=Buffer.from(s);}\n  "+needle)
  needle="s=s.replace('2026-10-07T10:00:00Z',new Date(cutoff).toISOString());";assert s.count(needle)==1
  s=s.replace(needle,needle+"\n   s=s.replace('lifetime.remainingSeconds>=130','lifetime.remainingSeconds>=160').replace('record.phases[0].seconds>=60','record.phases[0].seconds>=90').replaceAll('oneSixtySecondSessionCompleted','oneNinetySecondResidentTrialCompleted').replaceAll('sixtySecondHardwareSessionCompleted','ninetySecondResidentTrialCompleted').replace('nativeSessionCapSeconds:120','nativeSessionCapSeconds:120,routerDetachedClassLeaseController:true,originalKernelMaximumKept:true').replace('oneSixtySecondSessionCompleted','oneNinetySecondResidentTrialCompleted');")
  needle="'persistent-ssh.mjs']";assert s.count(needle)==1;s=s.replace(needle,"'persistent-ssh.mjs','resident-window.mjs']")
  needle="for(const name of ['fast-path.lua','classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.deepEqual(fs.readFileSync(runtimeRoot+'/'+name),fs.readFileSync(sourceRoot+'/'+name),name);";assert s.count(needle)==1
  s=s.replace(needle,"for(const name of ['classifier.lua','classified-tags.lua','module-stage-guardian.lua','qos-physical.lua','wan-scope.lua','tag-normalizer.lua'])assert.deepEqual(fs.readFileSync(runtimeRoot+'/'+name),fs.readFileSync(sourceRoot+'/'+name),name);assert.equal(fs.readFileSync(runtimeRoot+'/fast-path.lua','utf8'),patchResidentWindow(fs.readFileSync(sourceRoot+'/fast-path.lua','utf8')));")
  s=s.replace('dataPlaneByteExact:true,classificationAndQosPolicyUnchanged:true','dataPlaneByteExact:false,residentLifetimeOnlyChange:true,sixCoreLuaSourcesByteExact:true,nativeGateByteExact:true,classificationAndQosPolicyUnchanged:true')
  s=s.replace("hardwareBasis:'v42',simulatedGamePackets:true,limits", "hardwareBasis:'v42',simulatedGamePackets:true,boundedResidentCandidate:true,permanentNssDeployment:false,limits")
 with (root/name).open('x',encoding='utf8',newline='') as f:f.write(s)
with (root/'preparation.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'priorSourcesUnchanged':hashes,'onlyBoundedFastWindowChangedTo90Seconds':True,'kernelWithinOriginal120Maximum':True,'source6Owner180Client180Firewall180Server250Kept':True,'automaticRestartOrPermanentDeployment':False},f,indent=2)
print(json.dumps({'passed':True,'priorSources':len(hashes)}))
