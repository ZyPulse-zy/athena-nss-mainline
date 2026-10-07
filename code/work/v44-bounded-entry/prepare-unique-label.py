from pathlib import Path
import hashlib, json

w=Path(__file__).resolve().parents[2]
old=w/'work/v44-bounded-entry';new=w/'work/v44-unique-label-entry'
assert not new.exists();new.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
original={}
for name in ['entry.mjs','materialize.mjs','check-model.mjs','platform-preflight.mjs']:
    p=old/name;data=p.read_bytes();original[name]=sha(data)
    text=data.decode('utf8').replace('work/v44-bounded-entry','work/v44-unique-label-entry')
    if name=='materialize.mjs':
        needle=".replaceAll('v42-final','v44-final')"
        assert text.count(needle)==1
        text=text.replace(needle,".replaceAll('v42-final',runtimeRoot.slice(5)+'-final')")
    if name=='check-model.mjs':
        needle='const sourceHashes=Object.fromEntries('
        assert text.count(needle)==1
        regression=r"""const labelOf=p=>{
 const source=fs.readFileSync(p+'/read-final-health.mjs','utf8');
 const m=source.match(/current-audit-diagnostic\.mjs','([^']+)','prewrite'/);
 assert.ok(m,'Final readonly audit invocation is explicit');return m[1];
};
test('final audit label includes its complete fresh runtime namespace',()=>assert.equal(labelOf(root),root.slice(5)+'-final'));
const secondRoot='work/v44-run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
materialize(secondRoot,Date.now()+600000);
test('separate runtime final labels cannot collide in shared publication outputs',()=>{
 const source=fs.readFileSync('work/nss122/wait-publication-metadata.mjs','utf8');
 assert.ok(source.includes("'work/nss122/'+label+'-join-raw-private.json'"));
 assert.notEqual(labelOf(root),labelOf(secondRoot));
 assert.notEqual('work/nss122/'+labelOf(root)+'-join-raw-private.json','work/nss122/'+labelOf(secondRoot)+'-join-raw-private.json');
});
"""
        text=text.replace(needle,regression+needle)
    with (new/name).open('xb') as f:f.write(text.encode('utf8'))
assert all(sha((old/n).read_bytes())==d for n,d in original.items())
proof={'prepared':True,'originalV44EntryHashes':original,
       'change':'fresh runtime namespace in final readonly publication label',
       'provenFailure':'fixed v44-final label collided with prior readonly output under nss122',
       'twoOutputIsolationRegressionChecksAdded':True,
       'classificationQosDataPlaneAndSafetyCapsUnchanged':True,
       'noNewTrafficOrHardwareAttempt':True,'originalSourcesUnchanged':True}
with (new/'preparation.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps({'prepared':True,'newEntryRoot':'work/v44-unique-label-entry','onlyFinalAuditLabelAndRegressionChecksChanged':True,'newHardwareAttempt':False}))
