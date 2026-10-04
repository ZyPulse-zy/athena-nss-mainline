"""Change only tuple scanning: literal search followed by anchored matching."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent;root=here.parents[1]
old=(root/'work/nss29/classifier-core.lua').read_text()
a=""" for src,dst,sport,dport,packets,bytes in line:gmatch('src=(%d+%.%d+%.%d+%.%d+) dst=(%d+%.%d+%.%d+%.%d+) sport=(%d+) dport=(%d+) packets=(%d+) bytes=(%d+)') do
  tuples[#tuples+1]={src=src,dst=dst,sport=tonumber(sport),dport=tonumber(dport),packets=tonumber(packets),bytes=tonumber(bytes)}
 end"""
b=""" local tupleAt=1
 while true do
  local first=line:find('src=',tupleAt,true);if not first then break end
  local src,dst,sport,dport,packets,bytes,after=line:match('^src=(%d+%.%d+%.%d+%.%d+) dst=(%d+%.%d+%.%d+%.%d+) sport=(%d+) dport=(%d+) packets=(%d+) bytes=(%d+)()',first)
  if src then
   tuples[#tuples+1]={src=src,dst=dst,sport=tonumber(sport),dport=tonumber(dport),packets=tonumber(packets),bytes=tonumber(bytes)}
   tupleAt=after
  else tupleAt=first+1 end
 end"""
assert old.count(a)==1
new=old.replace(a,b)
(here/'classifier-core.lua').write_text(new,encoding='utf-8',newline='\n')
proof={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'candidateSha256':hashlib.sha256(new.encode()).hexdigest(),'onlyTupleScannerChanged':True,'policyAndTimeBoundsUnchanged':True,'old':a,'new':b}
(here/'core-delta.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items() if k not in ('old','new')}))
