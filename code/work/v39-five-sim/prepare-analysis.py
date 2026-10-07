from pathlib import Path

r=Path('work/v39-five-sim');s=Path('work/v38-sim/analyze-hardware.py').read_text()
def one(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b)
s=s.replace('work/v38-sim','work/v39-five-sim').replace('2979','3206')
one("proof['connectionCount']==3","proof['connectionCount']==5")
one("x['counts']['ecm_nss_ipv4/accelerated_count']==3","x['counts']['ecm_nss_ipv4/accelerated_count']==5")
one("[('tcp',6),('udp',17),('tcp2',6)]","[('tcp',6),('udp',17),('tcp2',6),('tcp3',6),('tcp4',6)]")
one("assert flow['tcp']['wanAffinity']!=flow['tcp2']['wanAffinity'] and len(wans) in [2,3]","assert wans==[1,2,3,4,5] and len({x['wanAffinity'] for x in flow.values()})==5")
one("for slot in ['tcp','tcp2']","for slot in ['tcp','tcp2','tcp3','tcp4']")
one("'ecmCountsThroughoutB':[3]","'ecmCountsThroughoutB':[5]")
one("'simultaneouslyAdmittedExactFlowCount':3,'fiveWanConcurrentFastPathProven':False","'simultaneouslyAdmittedExactFlowCount':5,'fiveWanConcurrentFastPathProven':True")
one("'twoSimultaneousBulkFlowsProven':True","'fourSimultaneousBulkFlowsProven':True")
one("'offeredLoadMbps':{'tcp':24,'tcp2':8,'total':32}","'offeredLoadMbps':{'tcp':8,'tcp2':8,'tcp3':8,'tcp4':8,'total':32}")
one("'fiveWanOrPermanentNssAcceptance':False","'fiveWanBoundedHardwareAcceptance':True,'permanentNssAcceptance':False")
one("'nativeGateAndQosUnchangedFromV20':True,'v35RankingAndRefusalFrameRetentionUsed':True","'fiveSlotNativeAndQosUnchangedFromV24':True,'v38OwnedAcquisitionMechanismAdapted':True")
with (r/'analyze-hardware.py').open('x',encoding='utf8') as f:f.write(s)
print('Five-flow analysis prepared; no success claimed before actual records.')
