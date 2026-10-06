from pathlib import Path
p=Path('work/nss129/fast-path.lua');s=p.read_text()
for old,new in [
 ('local session;local loaded=false;local tagBase','local session;local tagBase'),
 ('local began=now();local frame=classifier.observe()','local frame=classifier.observe()'),
 (';local nextCheck=0',''),
 ('record.preLearningProofAt=now()',''),
 ('record.tagEpochBaselineAt=now()',''),
 ('record.qosAtA=qos.snapshot();',''),
 ('record.qosAccelerated=qos.snapshot();',''),
 ('local fresh,learningDue=alignLearning(live)','local _,learningDue=alignLearning(live)'),
 (';loaded=true;stopped()',';stopped()'),
 (';loaded=false;stopped()',';stopped()'),
 ('record.initialAlignment={start=now(),stop=ending,probes={}}','record.initialAlignment={probes={}}'),
 ('Tag getter lacks bidirectional traffic','Tag traffic missing'),
 ('Tag counter snapshots do not overlap','Tag samples disjoint'),
 ('Startup tag mismatch exceeds observed boundary','Startup tag mismatch'),
 ('Native renewal receipt mismatch','Renewal mismatch'),
 ('Pinned instance changed during renewal','Renewal CT drift'),
 ('Terminal gate cannot acknowledge renewal','Terminal renewal'),
 ('Projection absence is not complete class evidence','Complete evidence required'),
 ('Actual BULK to BE required','BULK to BE required'),
 ('Remaining UDP class changed','UDP class changed'),
 ('Same CT/NAT/affinity required','CT identity drift'),
 ('New source without a renewal proposal','Renewal proposal missing'),
 ('Fresh learning margin lost after A','Learning margin lost'),
 ('Startup epoch exceeded getter deadline','Getter deadline'),
 ]:
    assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
p.write_text(s,encoding='utf-8',newline='\n')
