from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent;old=w/'work/v52-udp-preflight'
assert not (root/'preparation.json').exists()
names=['entry.mjs','materialize.mjs','fixture-startup.mjs','platform-preflight.mjs','ssh-phase.mjs','ssh-options.mjs','recheck-endpoint-readonly.mjs','udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1']
hashes={}
for name in names:
 blob=(old/name).read_bytes();hashes['work/v52-udp-preflight/'+name]=hashlib.sha256(blob).hexdigest()
 s=blob.decode().replace('v52-udp-preflight','v54-owned-control').replace('v52-run','v54-run')
 if name=='entry.mjs':
  needle="due=fs.statSync(setup.dir+'/server-deadline-private.json').mtimeMs+252000"
  assert s.count(needle)==1
  s=s.replace(needle,"due=Math.max(fs.statSync(setup.dir+'/server-launch-intent-private.json').mtimeMs+272000,fs.existsSync(setup.dir+'/firewall-launch-intent-private.json')?fs.statSync(setup.dir+'/firewall-launch-intent-private.json').mtimeMs+202000:0)")
 if name=='materialize.mjs':
  late="fs.writeFileSync(root+'/endpoint-setup-private.json',JSON.stringify({dir,unit,clientLaunchNotRequested:true})+'\\n',{flag:'wx'});"
  early="save('server-launch-intent-private',{at:new Date().toISOString(),unit,serverConfig:conf,sourceSha256:hash(serverSource),independentOsDeadlineSeconds:250});fs.writeFileSync(root+'/endpoint-setup-private.json',JSON.stringify({dir,unit,clientLaunchNotRequested:true})+'\\n',{flag:'wx'});"
  server="await ssh('systemd-run --unit='+unit"
  fw="const raw=await ssh('python3 -B -E -s -u -',guardian+"
  transform="if(name==='start-dallas.mjs'){let s=bytes.toString();const late="+json.dumps(late)+",server="+json.dumps(server)+",fw="+json.dumps(fw)+";assert.equal(s.split(late).length,2);assert.equal(s.split(server).length,2);assert.equal(s.split(fw).length,2);s=s.replace(late,'').replace(server,"+json.dumps(early)+"+server).replace(fw,\"save('firewall-launch-intent-private',{at:new Date().toISOString(),independentExpirySeconds:180});\"+fw);bytes=Buffer.from(s);}\n  if(name==='persistent-ssh.mjs'){bytes=fs.readFileSync(entryRoot+'/persistent-ssh.mjs');}\n  "
  needle="if(name==='pilot-supervisor.mjs'){";assert s.count(needle)==1;s=s.replace(needle,transform+needle)
  needle="'capture-no-client-closure.ps1']";assert s.count(needle)==2
  # Only the helper list includes the additional source, not the generated-template loop.
  helper="'ssh-options.mjs','recheck-endpoint-readonly.mjs','udp-probe.py','udp-probe.mjs','check-udp-path.mjs','recheck-partial-endpoint.mjs','capture-no-client-closure.ps1']"
  assert s.count(helper)==1;s=s.replace(helper,helper[:-1]+",'persistent-ssh.mjs']")
  s=s.replace("if(path.extname(name)==='.mjs'&&/spawn","if(name!=='persistent-ssh.mjs'&&path.extname(name)==='.mjs'&&/spawn")
 if name=='recheck-partial-endpoint.mjs':
  s=s.replace("assert.ok(Date.now()>=fs.statSync(setup.dir+'/server-deadline-private.json').mtimeMs+252000,'Original server deadline must have elapsed');", "const due=Math.max(fs.statSync(setup.dir+'/server-launch-intent-private.json').mtimeMs+272000,fs.existsSync(setup.dir+'/firewall-launch-intent-private.json')?fs.statSync(setup.dir+'/firewall-launch-intent-private.json').mtimeMs+202000:0);assert.ok(Date.now()>=due,'Original independent deadlines must have elapsed');")
  s=s.replace("const c=read(setup.dir+'/firewall-settings-private.json');", "const firewallIntent=fs.existsSync(setup.dir+'/firewall-launch-intent-private.json'),settingsExist=fs.existsSync(setup.dir+'/firewall-settings-private.json'),server=read(setup.dir+'/server-checkpoint-private.json');const boot=server.before.trim().split(/\\s+/).at(-1);assert.match(boot,/^[a-f0-9-]{36}$/);const c=settingsExist?read(setup.dir+'/firewall-settings-private.json'):{boot};assert.ok(!firewallIntent||settingsExist,'Firewall launch must have its original verified checkpoint');")
  s=s.replace("c['owner']+'-'", "c.get('owner','')+'-'")
  s=s.replace("'nss14-'+c.get('owner','')+'-'", "('nss14-'+c['owner']+'-' if 'owner' in c else 'nss14-')")
  s=s.replace("assert hashlib.sha256(canonical(rules).encode()).hexdigest()==c['baselineCanonicalSha256']", "if 'baselineCanonicalSha256' in c:assert hashlib.sha256(canonical(rules).encode()).hexdigest()==c['baselineCanonicalSha256']")
  s=s.replace("'baselineRestored':True", "'baselineRestored':'baselineCanonicalSha256' in c,'noFirewallWriteRequested':"+str(False))
  # Reflect the local launch intent rather than guessing an endpoint mutation.
  s=s.replace("'noFirewallWriteRequested':False", "'noFirewallWriteRequested':${!firewallIntent?'True':'False'}")
 with (root/name).open('x',encoding='utf8',newline='') as f:f.write(s)
source=w/'work/v53-control-framing/persistent-ssh-candidate.mjs';blob=source.read_bytes();hashes['work/v53-control-framing/persistent-ssh-candidate.mjs']=hashlib.sha256(blob).hexdigest()
s=blob.decode().replace('../v51-compact-entry/ssh-options.mjs','../v54-owned-control/ssh-options.mjs').replace('paced=false','paced=true')
with (root/'persistent-ssh.mjs').open('x',encoding='utf8',newline='') as f:f.write(s)
with (root/'preparation.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'priorSourcesUnchanged':hashes,'ownershipBeforeUnacknowledgedEndpointWrite':True,'boundedPrivateControlFramingAdded':True,'dataPlaneAndOriginalLifetimesUnchanged':True},f,indent=2)
print(json.dumps({'passed':True,'priorSources':len(hashes)}))
