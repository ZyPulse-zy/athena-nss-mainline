"""One variable: bounded per-observation memoization of pure IPv4 calculations."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent;root=here.parents[1]
old=(root/'work/nss29/classifier-core.lua').read_text()
a="""local function ip(v)
 if type(v)~='string' or not v:match('^%d+%.%d+%.%d+%.%d+$') then return false end
 for oct in v:gmatch('%d+') do if tonumber(oct)>255 then return false end end
 return true
end
local function ipnum(v) local n=0;for oct in v:gmatch('%d+') do n=n*256+tonumber(oct) end;return n end"""
b="""-- Cache pure address arithmetic within this observation only. CT metadata,
-- marks, NAT tuples, instance IDs and counters are still parsed every time.
local ipCache,numberCache={},{};local ipCacheCount,numberCacheCount=0,0
local function ipUncached(v)
 if type(v)~='string' or not v:match('^%d+%.%d+%.%d+%.%d+$') then return false end
 for oct in v:gmatch('%d+') do if tonumber(oct)>255 then return false end end
 return true
end
local function ip(v)
 if type(v)~='string'then return ipUncached(v)end
 local cached=ipCache[v];if cached~=nil then return cached end
 local result=ipUncached(v)
 if ipCacheCount<1024 then ipCache[v]=result;ipCacheCount=ipCacheCount+1 end
 return result
end
local function ipnum(v)
 local cached=numberCache[v];if cached~=nil then return cached end
 local result=0;for oct in v:gmatch('%d+')do result=result*256+tonumber(oct)end
 if numberCacheCount<1024 then numberCache[v]=result;numberCacheCount=numberCacheCount+1 end
 return result
end"""
reset="local function discover()\n ipCache,numberCache={},{};ipCacheCount,numberCacheCount=0,0"
assert old.count(a)==1 and old.count('local function discover()')==1
new=old.replace(a,b).replace('local function discover()',reset)
(here/'classifier-core-cache.lua').write_text(new,encoding='utf-8',newline='\n')
proof={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'candidateSha256':hashlib.sha256(new.encode()).hexdigest(),'onlyPureAddressCacheChanged':True,'policyAndTimeBoundsUnchanged':True,'old':a,'new':b,'resetOld':'local function discover()','resetNew':reset}
(here/'cache-delta.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
s=(here/'test-core.py').read_text().replace("core-delta.json","cache-delta.json").replace("(here/'classifier-core.lua')","(here/'classifier-core-cache.lua')").replace("parser-replay-private.lua","cache-replay-private.lua").replace("parser-replay-output.txt","cache-replay-output.txt").replace("parser-qualified.json","cache-qualified.json")
s=s.replace("assert old.replace(delta['old'],delta['new'])==new","assert old.replace(delta['old'],delta['new']).replace(delta['resetOld'],delta['resetNew'])==new")
(here/'test-cache.py').write_text(s,encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in proof.items() if k not in ('old','new','resetOld','resetNew')}))
