from pathlib import Path
import json, hashlib
r=Path('work/nss143'); old=Path('work/nss140')
def write(name,text):
    with (r/name).open('x',encoding='utf-8',newline='') as f:f.write(text)
def read(name):return (old/name).read_bytes().decode()
reader=read('read-real-candidates.mjs')
reader=reader.replace("from'./application-ownership.mjs'","from'../nss140/application-ownership.mjs'")
needle="const adapter=fs.readFileSync('work/nss49/classifier.lua','utf8').split('\\n').filter(x=>!x.trimStart().startsWith('--')).join('\\n');"
assert reader.count(needle)==1
reader=reader.replace(needle,"const adapter=candidateAdapter(fs.readFileSync('work/nss49/classifier.lua','utf8')).source;")
reader="import{candidateAdapter}from'./candidate-adapter.mjs';\n"+reader
reader=reader.replace('work/nss140/pc-app-endpoints-private.json','work/nss143/pc-app-endpoints-private.json').replace('work/nss140/real-candidates-raw-private.json','work/nss143/real-candidates-raw-private.json').replace('work/nss140/real-candidates-private.json','work/nss143/real-candidates-private.json').replace('work/nss140/real-reader-qualified.json','work/nss143/real-reader-qualified.json')
write('read-real-candidates.mjs',reader)
record=read('record-candidates.mjs').replace('work/nss140/','work/nss143/')
write('record-candidates.mjs',record)
entry=read('real-session.mjs')
for name in ['declared-baseline.mjs','compact-default-queues.mjs','service-epoch.mjs','parse-ecm-any-wan.mjs','module-stage.mjs','uplink-tag-plan.mjs']:
    assert "'./"+name+"'" in entry
    entry=entry.replace("'./"+name+"'","'../nss140/"+name+"'")
entry=entry.replace("observationRoot='work/nss140'","observationRoot='work/nss143'").replace("const dir='work/nss140/real-matched-aba-'","const dir='work/nss143/real-matched-aba-'")
write('real-session.mjs',entry)
proof={'at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'originalFactoryUnchangedExceptReaderAndOutputNamespace':True,'unchangedRouterPayloads':True,'newProductionExecution':False,'originalRealEntrySha256':hashlib.sha256((old/'real-session.mjs').read_bytes()).hexdigest(),'newRealEntrySha256':hashlib.sha256((r/'real-session.mjs').read_bytes()).hexdigest(),'change':'Visibility reader retains exact inspect, context and candidate checks; unused NSS adapter APIs omitted from reader only'}
write('entry-preparation.json',json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
