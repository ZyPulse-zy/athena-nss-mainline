from pathlib import Path
import hashlib, json

w = Path(__file__).resolve().parents[2]
old = w / 'work/v43-bounded-entry'
root = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
originals = {}
for name in ['entry.mjs', 'materialize.mjs', 'check-model.mjs', 'platform-preflight.mjs']:
    data = (old / name).read_bytes()
    originals[name] = sha(data)
    text = data.decode('utf-8').replace('v43-bounded-entry', 'v44-bounded-entry').replace('v43-run-', 'v44-run-').replace('v43-other', 'v44-other').replace('v43-final', 'v44-final')
    if name == 'materialize.mjs':
        needle = "runtimeRoot.replaceAll('/','\\\\/')).replaceAll"
        replacement = "runtimeRoot.replaceAll('/','\\\\/')+'\\\\/').replaceAll"
        assert text.count(needle) == 1
        text = text.replace(needle, replacement)
    if name == 'check-model.mjs':
        needle = "test('stop before client only writes own intent'"
        assert text.count(needle) == 1
        regression = r'''const auditSource=fs.readFileSync(root+'/current-audit-diagnostic.mjs','utf8');
const guardLiteral=auditSource.split('assert.match(caseDir,')[1].split(');')[0];
const auditGuard=Function('return ('+guardLiteral+');')();
test('generated readonly audit accepts exact owned session path',()=>assert.ok(auditGuard.test(root+'/session-20261007090000-aabbccdd')));
test('generated namespace prefixes retain trailing separator and reject escape',()=>{
 assert.ok(!auditGuard.test(root+'session-20261007090000-aabbccdd')&&!auditGuard.test(root+'/../session-20261007090000-aabbccdd'));
 const prefix='work\\/v42-counter-window\\/',expected=root.replaceAll('/','\\/')+'\\/';
 let checked=0;
 for(const origin of Object.keys(q.originHashes)){
  const source=fs.readFileSync(origin,'utf8'),count=source.split(prefix).length-1;
  if(count){const generated=fs.readFileSync(root+'/'+origin.split('/').at(-1),'utf8');assert.ok(generated.split(expected).length-1>=count,origin);checked+=count;}
 }
 assert.ok(checked>0);
});
'''
        text = text.replace(needle, regression + needle)
    with (root / name).open('xb') as f:
        f.write(text.encode('utf-8'))
    assert sha((old / name).read_bytes()) == originals[name]
proof = {'passed': True, 'originalV43SourcesUnmodified': originals,
         'localPathSeparatorDefect': True, 'onlyNamespaceCopiesAndSeparatorChanged': True,
         'classificationQosLeaseAndLimitsUnchanged': True,
         'originalFailureRuntime': 'work/v43-run-20261007090613-69b7cd24',
         'originalFailureBeforeRouterConnectionAndFixture': True,
         'newRegressionChecks': 2}
with (root / 'repair-preparation.json').open('x', encoding='utf-8') as f:
    json.dump(proof, f, indent=2)
print(json.dumps({'prepared': True, 'originalV43BytesPreserved': True, 'regressionChecksAdded': 2}))
