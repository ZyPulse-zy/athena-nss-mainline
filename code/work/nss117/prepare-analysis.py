from pathlib import Path
r=Path('work/nss117')
for name in ['health.mjs','read-final-physical.mjs']:(r/name).write_text(Path('work/nss115/'+name).read_text(encoding='utf-8').replace("work/nss115","work/nss117"),encoding='utf-8')
clock=Path('work/nss114/calibrate-clock.mjs').read_text(encoding='utf-8').replace('nss114','nss116');(r/'calibrate-clock.mjs').write_text(clock,encoding='utf-8')
s=Path('work/nss114/analyze-long.py').read_text(encoding='utf-8').replace('nss114-dual-physical-controlled-actual-v1','nss117-upload-controlled-actual-v1')
needle="report['uplinkUnderCongestionAccepted']=False;report['permanentClassifierPublicationUpTagZeroRetained']=True"
assert s.count(needle)==1
s=s.replace(needle,needle+"\nreport['bulkDirection']='upload';report['tcpMetric']='server-confirmed received bytes';report['localSubmittedBytesNotUsedForThroughput']=True")
(r/'analyze-long.py').write_text(s,encoding='utf-8')
(r/'prove-upstream.py').write_bytes(Path('work/nss114/prove-upstream.py').read_bytes())
print('Prepared server-confirmed upload metrics and new independent closure outputs')
