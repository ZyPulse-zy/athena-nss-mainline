"""Adapt the existing actual-record analysis to five exact, distinct WAN flows."""
from pathlib import Path

w = Path(__file__).resolve().parents[1]
s = (w / 'work/v20-five/analyze-hardware.py').read_text(encoding='utf8')
s = s.replace('work/v20-five', 'work/v23-fiveflow').replace('2533', '2672')
s = s.replace("proof['connectionCount']==3", "proof['connectionCount']==5")
s = s.replace("['accelerated_count']==3", "['accelerated_count']==5")
s = s.replace("['ecm_nss_ipv4/accelerated_count']==3", "['ecm_nss_ipv4/accelerated_count']==5")
s = s.replace("[('tcp',6),('udp',17),('tcp2',6)]", "[('tcp',6),('udp',17),('tcp2',6),('tcp3',6),('tcp4',6)]")
s = s.replace("assert flow['tcp']['wanAffinity']!=flow['tcp2']['wanAffinity'] and len(wans) in [2,3]", "assert wans==[1,2,3,4,5] and len(flow)==5")
s = s.replace("for slot in ['tcp','tcp2']", "for slot in ['tcp','tcp2','tcp3','tcp4']")
s = s.replace("'ecmCountsThroughoutB':[3]", "'ecmCountsThroughoutB':[5]")
s = s.replace("'simultaneouslyAdmittedExactFlowCount':3", "'simultaneouslyAdmittedExactFlowCount':5")
s = s.replace("'fiveWanConcurrentFastPathProven':False", "'fiveWanConcurrentFastPathProven':True")
s = s.replace("'twoSimultaneousBulkFlowsProven':True", "'fourSimultaneousBulkFlowsProven':True")
s = s.replace("'offeredLoadMbps':{'tcp':24,'tcp2':8,'total':32}", "'offeredLoadMbps':{'tcp':8,'tcp2':8,'tcp3':8,'tcp4':8,'total':32}")
s = s.replace("'nativeGateUnchangedFromV16':True,'onlyQosMapExpandedFromV19':True", "'fiveSlotNativeGateFromV21':True,'qosLuaUnchangedFromV20':True,'batchedPcInventoryOnlyFromV22':True,'localPathValidatorsCorrectedFromV23':True")
assert "connectionCount']==3" not in s and "accelerated_count']==3" not in s
with (w / 'work/v23-fiveflow/analyze-hardware.py').open('x', encoding='utf8') as f:
    f.write(s)
print('Five exact CT/WAN/tag proofs and original restoration/clock method analysis prepared; no new instrumentation')
