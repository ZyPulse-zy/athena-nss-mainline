"""Move only provisional TCP choice to the last pre-stage application frame."""
from pathlib import Path
import hashlib, json

w=Path(__file__).resolve().parents[2]
r=w/'work/v31-normal'; old=w/'work/v30-normal'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
q=read(old/'entry-qualified.json')
assert q['passed'] and not q['hardwareExecuted']
for f,h in q['sourceManifest'].items():assert sha((w/f).read_bytes())==h,f
rebase=lambda b:b.replace(b'work/v30-normal',b'work/v31-normal').replace(rb'work\/v30-normal\/',rb'work\/v31-normal\/')
changed={}
for name in read(old/'prepare-receipt.json')['copied']:
    data=rebase((old/name).read_bytes())
    if name=='epoch-driver.mjs':
        edits=[
          (b"import{mapClassifiedPair}from'./class-leaf-map.mjs';",b"import{mapClassifiedPair}from'./class-leaf-map.mjs';\r\nimport{selectAnchoredTriple}from'./normal-selection.mjs';"),
          (b"assert.deepEqual(preauditSelected,continuity.selected,'Automatic successor changed original CT/socket pair');",b"assert.deepEqual(preauditSelected.udp,continuity.selected.udp,'Original CS2 CT/socket identity changed');"),
          (b"  // Choose only application-owned identities visible both before and after the\r\n  // full audit. The native gate still pins one exact TCP and UDP for the epoch.",b"  // Retain the original game; choose current owned BULK sockets after the audit.\r\n  // The final immutable TCP identities are selected after checkpoint download."),
          (b"  selected=selectionFrame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));\r\n  assert.ok(selected,'Controlled exact pair changed after original full audit');",b"  selected=selectAnchoredTriple(selectionFrame,preauditSelected.udp)[0];\r\n  assert.ok(selected,'Original CS2 or current two-WAN Steam BULK candidates missing after full audit');"),
          (b"currentSequence:selectionFrame.sourceSequence,selected});",b"currentSequence:selectionFrame.sourceSequence,originalGameIdentityRetained:true,provisionalBulkSelectedAfterOriginalFullAudit:true,selected});"),
          (b"   assert.equal(frame.producer,selectionFrame.producer);assert.ok(frame.sourceSequence>=selectionFrame.sourceSequence);selected=frame.pairs.find(p=>JSON.stringify(p)===JSON.stringify(preauditSelected));assert.ok(selected,'Controlled exact pair changed after checkpoint');",b"   assert.equal(frame.producer,selectionFrame.producer);assert.ok(frame.sourceSequence>=selectionFrame.sourceSequence);\r\n   selected=selectAnchoredTriple(frame,selected.udp,{tcp:selected.tcp.wan,tcp2:selected.tcp2.wan})[0];\r\n   assert.ok(selected,'Original CS2 or current same-WAN Steam BULK candidates missing after checkpoint');")
        ]
        for a,b in edits:
            assert data.count(a)==1,a.decode()
            data=data.replace(a,b)
        changed[name]='original UDP retained; TCP chosen after audit and finally after checkpoint, before independent stage'
    elif name=='module-stage.mjs':
        a=b"import {verifyCandidate,validateRefinement} from './candidate-policy.mjs';"
        b=b"import {verifyCandidate} from './candidate-policy.mjs';\r\nimport{validatePreStageRefinement as validateRefinement}from'./normal-refinement.mjs';"
        assert data.count(a)==1; data=data.replace(a,b)
        changed[name]='only pre-detached-stage refinement import; original candidate policy remains immutable'
    with (r/name).open('xb') as f:f.write(data)
for name in ('native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','normal-policy-qualified.json'):
    with (r/name).open('xb') as f:f.write((old/name).read_bytes())
receipt={'passed':True,'oldRoot':'work/v30-normal','oldHashes':{f:sha((w/f).read_bytes()) for f in q['sourceManifest']},
         'copied':read(old/'prepare-receipt.json')['copied'],'changed':changed,'oldQualifiedSourcesUnmodified':True}
with (r/'prepare-receipt.json').open('x',encoding='utf8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'copied':len(receipt['copied']),'changed':list(changed),'noRouterWrites':True}))
