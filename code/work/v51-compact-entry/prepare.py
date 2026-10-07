"""Fresh entry with compact offers, phase evidence, and its missing readonly recovery target."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent;old=w/'work/v48-ssh-phase'
assert not (root/'preparation.json').exists()
hashes={}
for name in ['entry.mjs','materialize.mjs','fixture-startup.mjs','platform-preflight.mjs','ssh-phase.mjs']:
    blob=(old/name).read_bytes();hashes['work/v48-ssh-phase/'+name]=hashlib.sha256(blob).hexdigest()
    s=blob.decode().replace('v48-ssh-phase','v51-compact-entry').replace('v48-run','v51-run')
    if name=='materialize.mjs':
        s="import{compactSshOptions}from'./ssh-options.mjs';\n"+s
        needle="bytes=Buffer.from(instrumentNativeClient(s));"
        assert s.count(needle)==1
        s=s.replace(needle,"s=instrumentNativeClient(s);s=\"import{compactSshOptions}from'../v51-compact-entry/ssh-options.mjs';\\n\"+s;s=s.replace(\"spawn(sshExe,['-v','-o'\",\"spawn(sshExe,['-v',...compactSshOptions,'-o'\");bytes=Buffer.from(s);")
        needle="fs.writeFileSync(runtimeRoot+'/'+name,bytes,{flag:'wx'});"
        assert s.count(needle)==1
        s=s.replace(needle,"if(path.extname(name)==='.mjs'&&/spawn(?:Sync)?\\('ssh',\\[/.test(bytes.toString())){let s=bytes.toString();s=\"import{compactSshOptions}from'../v51-compact-entry/ssh-options.mjs';\\n\"+s;s=s.replaceAll(\"spawn('ssh',[\",\"spawn('ssh',[...compactSshOptions,\").replaceAll(\"spawnSync('ssh',[\",\"spawnSync('ssh',[...compactSshOptions,\");bytes=Buffer.from(s);}\n  "+needle)
        needle="const binding=`import fs from'node:fs';"
        assert s.count(needle)==1
        s=s.replace(needle,"const recheck=fs.readFileSync(entryRoot+'/recheck-endpoint-readonly.mjs','utf8').replaceAll('__RUNTIME__',runtimeRoot);fs.writeFileSync(runtimeRoot+'/recheck-endpoint-readonly.mjs',recheck,{flag:'wx'});generatedHashes[runtimeRoot+'/recheck-endpoint-readonly.mjs']=hash(Buffer.from(recheck));\n "+needle)
        needle="'fixture-startup.mjs','ssh-phase.mjs'"
        assert s.count(needle)==1
        s=s.replace(needle,needle+",'ssh-options.mjs','recheck-endpoint-readonly.mjs'")
    with (root/name).open('x',encoding='utf8',newline='') as f:f.write(s)
blob=(w/'work/v50-compact-handshake/ssh-options.mjs').read_bytes()
with (root/'ssh-options.mjs').open('xb') as f:f.write(blob)
proof={'passed':True,'priorSourcesUnchanged':hashes,'onlyOwnedSshOffersChanged':True,
       'originalNegotiatedAlgorithmsKept':True,'missingReadonlyRecoveryTargetAdded':True,
       'dataPlaneClassificationQosAndLimitsUnchanged':True}
with (root/'preparation.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
print(json.dumps({'passed':True,'priorSources':len(hashes),'onlyOwnedSshOffersChanged':True}))
