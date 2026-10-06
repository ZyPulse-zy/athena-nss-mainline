from pathlib import Path
p=Path('work/nss129/fast-path.lua');s=p.read_text()
a=s.index('      assert(e.sameSourceCompleteFrame');b=s.index('      record.actualReclassification=',a)
body=s[a:b].replace('record.adapterProducer','producer')
function="""function M.verifyReclassification(comparison,producer)
 assert(comparison.action=='RETIRE_EXACT_SELECTED_SLOTS'and #comparison.affected==1 and comparison.affected[1]=='tcp','Unexpected retirement scope')
 local e=assert(comparison.evidence and comparison.evidence.completeSelected,'Projection absence is not complete class evidence')
"""+body+" return e\nend\n"
s=s[:a]+"      M.verifyReclassification(comparison,record.adapterProducer)\n"+s[b:]
s=s.replace('function M.new(',function+'function M.new(',1)
p.write_text(s,encoding='utf-8',newline='\n')
p=Path('work/nss129/controlled-session.mjs');s=p.read_text().replace("mode:'aba',output:dir","mode,output:dir");p.write_text(s,encoding='utf-8',newline='\n')
