from pathlib import Path
import hashlib,json
r=Path('work/nss147');old=Path('work/nss146')
p=json.loads((old/'entry-qualified.json').read_text())
for file,digest in p['sourceManifest'].items():
    src=Path(file);b=src.read_bytes();assert hashlib.sha256(b).hexdigest()==digest
    if src.name.startswith(('prepare','qualify','fast-models')) or src.name in ['session-binding.mjs','phase-models.lua','consumer-models.lua']:
        continue
    s=b.replace(b'nss146',b'nss147').replace(b'NSS146',b'NSS147')
    assert s.replace(b'nss147',b'nss146').replace(b'NSS147',b'NSS146')==b
    if src.name=='classifier.lua':
        a=b'function A.compareObserved()return assert(activeInstance).compareObserved()end'
        z=b'function A.compareObserved(closed)return assert(activeInstance).compareObserved(closed)end'
        assert s.count(a)==1;s=s.replace(a,z)
    with (r/src.name).open('xb') as f:f.write(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json']:
    with (r/name).open('xb') as f:f.write((old/name).read_bytes())
model=(old/'phase-models.lua').read_text()
a=' function A.compareObserved(closed)return Consumer.compareEpoch(epoch,latest,c,at,closed)end'
z=' local activeInstance={compareObserved=function(closed)return Consumer.compareEpoch(epoch,latest,c,at,closed)end}\n __FACADE__'
assert model.count(a)==1;model=model.replace(a,z)
with (r/'phase-models.lua').open('x',encoding='utf-8') as f:f.write(model)
q=(old/'qualify-v5.mjs').read_text().replace('nss146','nss147').replace('NSS146','NSS147')
q=q.replace("from'../nss145/session-binding.mjs'","from'../nss146/session-binding.mjs'")
needle=".replace('function out.compareObserved(closed)','function out.compareObserved()')"
assert q.count(needle)==1
q=q.replace(needle,".replace('function A.compareObserved(closed)return assert(activeInstance).compareObserved(closed)end','function A.compareObserved()return assert(activeInstance).compareObserved()end')"+needle)
q=q.replace(" .replace('__CONSUMER__',()=>modelConsumer)"," .replace('__CONSUMER__',()=>modelConsumer)\n .replace('__FACADE__',()=>cut(consumer,'function A.compareObserved(','\\nfunction A.resampleClosed('))")
a=q.index('const consumerCode=');b=q.index('const c=await connectRouter();',a)
q=q[:a]+"const previousProof=JSON.parse(fs.readFileSync('work/nss146/entry-qualified.json'));const currentConsumerPart=consumer.slice(0,consumer.indexOf('local describeSelection='));assert.equal(currentConsumerPart,fs.readFileSync('work/nss146/classifier.lua','utf8').slice(0,fs.readFileSync('work/nss146/classifier.lua','utf8').indexOf('local describeSelection=')));\n"+q[b:]
a=q.index('try{const cr=JSON.parse(');b=q.index('const raw=receipt(await c.run(enc.command),enc);',a)
q=q[:a]+"try{consumerModels=previousProof.consumerModels;assert.ok(consumerModels.passed&&consumerModels.checks===8);"+q[b:]
q=q.replace('controlledClosedPhaseCorrection:true','controlledClosedPhaseCorrection:true,actualFacadeIncluded:true')
q=q.replace('changedPhaseModelChecks:models.checks','actualFacadeIncluded:true,changedPhaseModelChecks:models.checks')
with (r/'qualify.mjs').open('x',encoding='utf-8') as f:f.write(q)
binding=(old/'session-binding.mjs').read_text().replace("from'../nss145/session-binding.mjs'","from'../nss146/session-binding.mjs'").replace('work/nss146/entry-qualified.json','work/nss147/entry-qualified.json')
binding=binding.replace('p.controlledClosedPhaseCorrection&&!p.productionExecution','p.controlledClosedPhaseCorrection&&p.actualFacadeIncluded&&!p.productionExecution')
with (r/'session-binding.mjs').open('x',encoding='utf-8') as f:f.write(binding)
print(json.dumps({'prepared':True,'change':'Forward closed software comparison flag through exact adapter facade','oldFailurePreserved':True,'nativeLeasesAndClassChecksUnchanged':True,'routerWrites':False}))
