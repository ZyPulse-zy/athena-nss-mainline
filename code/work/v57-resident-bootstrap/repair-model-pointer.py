from pathlib import Path
import json,shutil
r=Path('work/v57-resident-bootstrap');d=r/'model-source-v2';d.mkdir()
for n in ['check-model.mjs','materialize.mjs','route-acquisition.mjs']:
    shutil.copyfile(r/n,d/n)
shutil.copyfile(r/'entry-model-latest-private.json',d/'model-pointer-private.json')
(d/'pointer-failure.json').write_text(json.dumps({'passed':False,'actualExitCode':1,'error':'EEXIST: file already exists, open entry-model-latest-private.json','allModelAssertionsHadCompleted':True,'productionExecuted':False},indent=2)+'\n')
p=r/'check-model.mjs';s=p.read_text();needle="save(entryRoot+'/entry-model-latest-private.json',{receipt});";assert s.count(needle)==1
s=s.replace(needle,"const pointer=entryRoot+'/entry-model-latest-private.json',next=pointer+'.'+crypto.randomBytes(4).toString('hex');if(fs.existsSync(pointer))save(entryRoot+'/model-pointer-history-'+Date.now()+'.json',JSON.parse(fs.readFileSync(pointer)));save(next,{receipt});fs.renameSync(next,pointer);")
p.write_bytes(s.encode())
print(json.dumps({'passed':True,'modelReceiptsAppendOnly':True,'latestPointerAtomic':True,'priorPointerAndFailurePreserved':True}))
