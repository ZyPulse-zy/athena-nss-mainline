"""Select current owned TCPs after readonly prerequisites, before WAN scope freezes."""
from pathlib import Path
import hashlib, json

w=Path(__file__).resolve().parents[2]
r,old=w/'work/v34-normal',w/'work/v33-normal'
sha=lambda b:hashlib.sha256(b).hexdigest()
q=json.loads((old/'entry-qualified.json').read_text())
for f,h in q['sourceManifest'].items():assert sha((w/f).read_bytes())==h,f
rebase=lambda b:b.replace(b'work/v33-normal',b'work/v34-normal').replace(rb'work\/v33-normal\/',rb'work\/v34-normal\/')
copied=[]
for f in q['sourceManifest']:
 p=w/f
 if p.suffix not in ('.mjs','.lua','.ps1') or p.name in ('qualify-entry.mjs','session-binding.mjs'):continue
 data=rebase(p.read_bytes())
 if p.name=='session.mjs':
  prior=b"Date.parse('2026-10-07T03:30:00Z')";assert data.count(prior)==1
  data=data.replace(prior,b"Date.parse('2026-10-07T04:30:00Z')")
 if p.name=='epoch-driver.mjs':
  text=data.decode()
  text=text.replace("import{selectAnchoredTriple}from'./normal-selection.mjs';", "import{selectAnchoredTriple}from'./normal-selection.mjs';\nimport{selectPreparedTriple}from'./prepared-selection.mjs';")
  text=text.replace('const selectionFrame=JSON.parse','let selectionFrame=JSON.parse')
  begin=text.index("  const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8');")
  end=text.index('  const owner=crypto.randomBytes(16)',begin)
  text=text[:begin]+'''  // These reads grant no NSS authority. Discover candidate WANs before fixing TCP slots.
  const source=fs.readFileSync(root+'/read-prerequisites.lua','utf8'),prepared=new Map();
  const candidateWans=[...new Set([selected.udp.wan,...selectionFrame.bulk.map(f=>f.identity.wan)])].sort();
  assert.ok(candidateWans.length>=2&&candidateWans.length<=5);
  for(const w of candidateWans){const e=encode("/usr/bin/lua - "+w+" <<'NSS27_REAL_PREREQUISITES'\\n"+source+"\\nNSS27_REAL_PREREQUISITES\\n");const raw=receipt(await c.run(e.command),e);assert.equal(raw.code,0,raw.stderr);const q=JSON.parse(raw.stdout);save('prepared-prerequisites-wan-'+w+'-private',q);assert.equal(q.wan,w);assert.equal(q.status.l3_device,'rpwan'+w);prepared.set(w,q);}
  const pin=JSON.parse(fs.readFileSync('work/nss16/qos-capacity-private.json'));const up=JSON.parse(fs.readFileSync('work/nss140/uplink-capacity-private.json'));assert.equal(up.device,'wan');assert.equal(up.ifindex,6);
  const preparedReference={boot:pin.boot.trim(),stateMajor:prepared.get(selected.tcp.wan).stateMajor};
  let prerequisites,wan;
'''+text[end:]
  before="  assert.ok(fresh.udp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.udp))&&fresh.tcp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.tcp))&&fresh.tcp.some(f=>JSON.stringify(convert(f))===JSON.stringify(selected.tcp2)),'Exact controlled socket pair changed before staging');"
  assert text.count(before)==1
  after="""  selected=selectPreparedTriple(fresh,preauditSelected.udp,[...prepared.values()],preparedReference)[0];
  assert.ok(selected,'Original CS2 or current two-WAN Steam BULK with prepared native prerequisites missing before WAN freeze');
  selectionFrame=fresh;
  prerequisites=[...new Set([selected.tcp.wan,selected.udp.wan,selected.tcp2.wan])].map(w=>prepared.get(w));wan=prerequisites[0];
  for(const q of prerequisites){assert.equal(q.boot,wan.boot);assert.equal(q.stateMajor,wan.stateMajor);}
  assert.equal(up.boot,wan.boot);assert.equal(pin.boot.trim(),wan.boot);
  save('final-selection-before-wan-freeze-private',{passed:true,observedAt:new Date().toISOString(),producer:fresh.producer,sourceSequence:fresh.sourceSequence,selected,nativePrerequisitesPreparedFirst:true,wanScopeFrozenOnlyNow:true,installedGateRetargeted:false});"""
  text=text.replace(before,after)
  # The entire checkpoint/refinement/owner/upload/retirement path retains its original bytes.
  tail='  context=await beginStage('
  assert text[text.index(tail):]==data.decode()[data.decode().index(tail):]
  data=text.encode()
 with (r/p.name).open('xb') as f:f.write(data)
 copied.append(p.name)
for name in ('native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json','last-selection-qualified.json'):
 with (r/name).open('xb') as f:f.write((old/name).read_bytes())
data=(old/'session-binding.mjs').read_bytes().replace(b'v32-normal',b'v33-normal').replace(b'v33-normal/entry',b'v34-normal/entry')
# Keep the inherited verifier on v33 and the new manifest on v34.
assert b"from'../v33-normal/session-binding.mjs'" in data
with (r/'session-binding.mjs').open('xb') as f:f.write(data)
receipt={'passed':True,'oldRoot':'work/v33-normal','oldHashes':q['sourceManifest'],'copied':copied,
 'newCutoff':'2026-10-07T04:30:00Z','onlyReadPreparationAndInitialSelectionOrderChanged':True,
 'postCheckpointRefinementAndDetachedOwnerUnchanged':True,'dataPlaneChanged':False,
 'newFlowsOrWanAccelerationScopeAdded':False,'hardwareExecuted':False,'routerWrites':False}
with (r/'prepare-receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'copied':len(copied),'dataPlaneChanged':False,'routerWrites':False}))
