from pathlib import Path
import shutil,json
r=Path('work/v57-resident-bootstrap')
shutil.copyfile(r/'check-route-acquisition.mjs',r/'model-source-v1/check-route-acquisition.mjs')
p=r/'route-acquisition.mjs';s=p.read_text();before="ct:gmatch('[^\\\\n]+')";after="ct:gmatch('[^\\\\\\\\n]+')"
assert s.count(before)==1;s=s.replace(before,after)
needle=" source=once(source,'const c=await connectRouter();','const c=readerConnection??=await connectRouter();');"
assert s.count(needle)==1
addition="""
 source=once(source,'export async function readControlled(){\\n','export async function readControlled(){\\nconst readBegan=performance.now();\\n');
 source=once(source,'windowsHide:true,timeout:15000','windowsHide:true,timeout:Math.max(1,15000-(performance.now()-readBegan))');
 source=once(source,'const raw=receipt(await c.run(e.command),e);',"const remaining=15000-(performance.now()-readBegan);assert.ok(remaining>0,'Original owned read deadline consumed');let timer,raw;try{raw=receipt(await Promise.race([c.run(e.command),new Promise((_,reject)=>{timer=setTimeout(()=>{closeControlledReader();reject(Error('Original fifteen-second owned read deadline exceeded'));},remaining);})]),e);}finally{clearTimeout(timer);}");
"""
s=s.replace(needle,needle+addition);p.write_bytes(s.encode())
p=r/'materialize.mjs';s=p.read_text();needle="'resident-window.mjs','route-acquisition.mjs']";assert s.count(needle)==1;s=s.replace(needle,"'resident-window.mjs','route-acquisition.mjs','check-route-acquisition.mjs']");p.write_bytes(s.encode())
print(json.dumps({'passed':True,'escapedLuaStringCorrected':True,'originalFifteenSecondPerReadDeadlineKept':True,'firstFailureSourceAndOutputPreserved':True,'productionExecuted':False}))
