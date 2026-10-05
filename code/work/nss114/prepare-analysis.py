from pathlib import Path
r=Path('work/nss114')
clock=Path('work/nss110/calibrate-clock.mjs').read_text(encoding='utf-8').replace('nss110','nss114');(r/'calibrate-clock.mjs').write_text(clock,encoding='utf-8')
s=Path('work/nss100/analyze-long.py').read_text(encoding='utf-8').replace("'schema':'nss100-long-controlled-actual-v1'","'schema':'nss114-dual-physical-controlled-actual-v1'")
s=s.replace("'upstreamQosVerified':False","'upstreamQosVerified':json.loads((case/'actual-upstream-proof.json').read_text())['passed']")
needle="(case/'actual-long-metrics.json').write_text(json.dumps(report,indent=2)+'\\n')"
assert s.count(needle)==1
addition="""upbase=qdisc(s['qosAccelerated']['uplink']['qdisc']);upend=qdisc(s['qosAfterRetirement']['uplink']['qdisc'])
report['uplinkLeafAcrossBNearbySnapshots']={k:{'delta':{n:upend[k][n]-upbase[k][n]for n in ('bytes','packets','dropped','overlimits')},'beforeBacklogPackets':upbase[k]['backlogPackets'],'afterBacklogPackets':upend[k]['backlogPackets']}for k in ('8e05:','8e06:')}
report['uplinkPhysicalDevice']='wan';report['uplinkRootSharedByMacVlans']=True;report['unselectedPhysicalFallbackMbps']=950
report['uplinkUnderCongestionAccepted']=False;report['permanentClassifierPublicationUpTagZeroRetained']=True
"""
s=s.replace(needle,addition+needle);(r/'analyze-long.py').write_text(s,encoding='utf-8')
print('Prepared actual bidirectional leaf analysis; bound runtime sources unchanged')
