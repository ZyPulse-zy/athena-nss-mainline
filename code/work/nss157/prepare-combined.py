"""Combine two already exercised retirement paths; no production execution."""
from pathlib import Path
r=Path(__file__).resolve().parent
old=r.parent/'nss149';exitpath=r.parent/'nss155'
s=(exitpath/'fast-path.lua').read_text(encoding='utf-8');known=(old/'fast-path.lua').read_text(encoding='utf-8')
a=known.index('function M.verifyReclassification(');b=known.index('function M.new(',a);verify=known[a:b]
s=s.replace('function M.new(',verify+'function M.new(',1).replace('local active=false\n','local active=false;local retire\n',1)
a=known.index(' retire=function(C)');b=known.index(' local function tick(name)',a);retire=known[a:b]
anchor=' local function tick(name)';assert s.count(anchor)==1;s=s.replace(anchor,retire+anchor)
before="if active then return{terminalReason='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED',comparison=C}end";assert s.count(before)==1
s=s.replace(before,"if active then\n    local supported=pcall(M.verifyReclassification,C,R.adapterProducer)\n    if supported then retire(C);return{terminalReason='AUTHENTICATED_BULK_TO_BE',comparison=C}end\n    return{terminalReason='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED',comparison=C}\n   end")
s=s.replace('exactSingleCiRetirementClaimed=false}', 'exactSingleCiRetirementClaimed=R.classChangeTestCompleted==true}')
s=s.replace('R.lifecycleVersion=155;','R.lifecycleVersion=157;')
p=r/'fast-path.lua';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Precise supported-class CI retirement plus whole-pair invalidation assembled offline; not yet qualified or staged.')
