"""Replay the same eight synthetic journal scenarios in native target Lua."""
from pathlib import Path
import hashlib,json,difflib
here=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
old=(here/'original-backend.lua').read_text();new=(here/'candidate-backend.lua').read_text();a=old.splitlines(keepends=True);b=new.splitlines(keepends=True)
patches=[]
for group in difflib.SequenceMatcher(None,a,b,autojunk=False).get_grouped_opcodes(3):
    first,last=group[0],group[-1];x=''.join(a[first[1]:last[2]]);y=''.join(b[first[3]:last[4]])
    assert old.count(x)==1 and ']=======]'not in x+y;patches.append([x,y])
rebuilt=old
for x,y in patches:rebuilt=rebuilt.replace(x,y)
assert rebuilt==new
loader=r'''local base=assert(arg[1]);local own=assert(dofile(base..'/owned.lua'));local f=assert(io.open(base..'/backend.lua'));local backendText=f:read(16385);f:close();assert(#backendText<=16384)
local function replace(a,b)local x,y=backendText:find(a,1,true);assert(x and not backendText:find(a,y+1,true));backendText=backendText:sub(1,x-1)..b..backendText:sub(y+1)end
'''
for x,y in patches:loader+='replace([=======['+x+']=======],[=======['+y+']=======])\n'
loader+='local B=assert(loadstring(backendText))()\n'
code=(here/'expiry-journal-replay.lua').read_text();first=code.split('\n',1)[0];assert first.startswith('local here=assert(arg[1])');code=code.replace(first,loader,1)
code+='\nprint(require("luci.jsonc").stringify({passed=true,checks=#scenarios,compiledBackend=backendText}))\n'
(here/'expiry-journal-native.lua').write_text(code,encoding='utf-8',newline='\n')
proof={'passed':True,'fixtureSha256':sha(code.encode()),'backendSha256':sha(new.encode()),'sameEightCases':True,'nativeQueueIOAndPublicationsMocked':True,'realMutationChildExecuted':False,'installed':False,'routerWrites':False}
(here/'expiry-journal-native-prepared.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
