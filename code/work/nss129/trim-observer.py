from pathlib import Path
import json
p=Path('work/nss129/fast-path.lua');s=p.read_text()
old="counts={},cpu=read('/proc/stat',16384),softnet=read('/proc/net/softnet_stat',16384),interfaces={}"
assert s.count(old)==1;s=s.replace(old,'counts={}')
begin=s.index("  for _,d in ipairs({'rpwan1'")
end=s.index("  assert(r.stop6",begin)
s=s[:begin]+s[end:]
p.write_text(s,encoding='utf-8',newline='\n')
# Preserve the first passing models and syntax independently of the sizing failure.
r=Path('work/nss129');failed=r/'failed-qualification-v1';failed.mkdir()
for name in ['retirement-model-raw-private.json','fast-syntax-private.json']:
    (failed/name).write_bytes((r/name).read_bytes())
(failed/'result.json').write_text(json.dumps({'passed':False,'modelsPassed':True,'fastSyntaxPassed':True,'failure':'Guarded payload exceeds unchanged 73728 byte limit','productionWrites':False})+'\n')
p=r/'qualify.mjs';s=p.read_text().replace('retirement-model-raw-private.json','retirement-model-v2-raw-private.json').replace('fast-syntax-private.json','fast-syntax-v2-private.json');p.write_text(s,encoding='utf-8',newline='\n')
