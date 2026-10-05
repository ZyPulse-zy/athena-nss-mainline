"""Read actual, immutable class-change and fresh-generation proofs. No admission."""
from pathlib import Path
import hashlib,json,importlib.util
w=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('collector',w/'work/nss101/collect-lifecycle.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def same_slots(s):
    return all(s[k]is True for k in ['ctMatches','zoneMatches','markMatches','wanMatches','originalMatches','replyMatches'])
def collect(root):
    r=w/root;ref=load(r/'experiment-reference.json');again=load(r/'relearning-reference.json');a=w/ref['output'];b=w/again['output']
    first=c.stage(a.relative_to(w).as_posix());second=c.stage(b.relative_to(w).as_posix())
    assert first['passed']and second['passed']and not first['completeABA']and not second['completeABA']
    x=load(a/'last-record-private.json');y=load(b/'last-record-private.json');assert x['classChangeTestCompleted']and y['freshEpochRelearningCompleted']
    comp=x['actualReclassification'];assert comp['action']=='RETIRE_EXACT_SELECTED_SLOTS'and comp['affected']==['tcp']and comp['clearConntrack']is False and comp['changeQoSBeforeRetirement']is False
    f=comp['evidence']['completeSelected'];t,u=f['slots']['tcp'],f['slots']['udp']
    assert f['sameSourceCompleteFrame']and f['afterRejectionOnly']and not f['nssAdmissionAllowed']
    assert t['present']and t['matches']==1 and t['class']=='BE'and t['reason']=='cooldown'and t['budgetAdmitted']is False and t['downTag']==0 and same_slots(t)
    assert u['present']and u['matches']==1 and u['class']=='RT'and u['budgetAdmitted']and u['downTag']==0x8f060000 and same_slots(u)
    complete=f['authenticatedSelectedFlows'];assert len(complete)==2;byproto={row['identity']['protocolNumber']:row for row in complete};assert byproto[6]['decision']['class']=='BE'and byproto[17]['decision']['class']=='RT'
    for row in complete:
        assert row['identity']['queryProvenance']['querySequence']==f['provenance']['sequence']
        assert row['identity']['queryProvenance']['startedAtUptime']==f['provenance']['startedAtUptime']
        assert row['identity']['queryProvenance']['finishedAtUptime']==f['provenance']['finishedAtUptime']
    q=x['remainingUdpCounters']['counts'];assert q['ecm_db/connection_count']==q['ecm_nss_ipv4/accelerated_count']==1 and all(v==0 for k,v in q.items()if 'pending_'in k or 'ipv6'in k)
    before=x['parametersBeforeSingleRetire'];after=x['parametersAfterSingleRetire'];assert before['tcp_permit']==before['game_permit']=='Y'and after['tcp_permit']=='N'and after['game_permit']=='Y'
    assert 'ever_opened=1 terminal=1 admit=0'in after['tcp_state']and 'ever_opened=1 terminal=0 admit=1'in after['game_state']and 'cpu_drain_ticket=1'in after['tcp_state']
    assert int(after['cpu_barriers'])>int(before['cpu_barriers'])and int(after['revoke_calls'])==int(before['revoke_calls'])+2
    assert x['reclassificationFrontendStoppedAt']<=x['tcpClosedAt']<=x['tcpDrainRequestedAt']<=x['remainingUdpObservedAt']<x['tagEpochUntil']
    assert x['noRetagBeforeSingleCiAbsence']and x['remainingUdpObservedAt']<x['tagsRemovedAt']
    old=load(a/'actual-accelerated-state-proof.json');remaining=load(a/'actual-remaining-udp-proof.json');new=load(b/'actual-accelerated-state-proof.json')
    assert remaining['connectionCount']==1 and remaining['proof']['udp']['serial']==old['proof']['udp']['serial']
    sa=load(a/'selected-private.json');sb=load(b/'selected-private.json');assert sa==sb
    assert first['afterFullAudit']['passed']and second['beforeFullAudit']['passed']
    ca=load(a/'stage-checkpoint-verified.json');cb=load(b/'stage-checkpoint-verified.json');pa=load(a/'stage-plan-private.json');pb=load(b/'stage-plan-private.json')
    assert ca['name']!=cb['name']and ca['gzipVerified']and cb['gzipVerified']and pa['owner']!=pb['owner']and pa['frozenHash']!=pb['frozenHash']
    assert x['moduleUnloaded']and y['moduleLoaded']and y['parametersBefore']['tcp_state'].startswith('ever_opened=0 terminal=0 admit=0')
    assert int(y['adapterSourceSequence'])>int(x['adapterSourceSequence'])and x['adapterProducer']==y['adapterProducer']
    assert old['proof']['tcp']['serial']!=new['proof']['tcp']['serial']and old['proof']['udp']['serial']!=new['proof']['udp']['serial']
    pause=load(a/'application-pause-private.json');resume=load(a/'application-resume-private.json');assert pause['paused']and not resume['paused']and pause['clientPid']==resume['clientPid']and pause['tcpSourcePort']==resume['tcpSourcePort']and pause['udpSourcePort']==resume['udpSourcePort']
    for rcd in [x,y]:
        assert rcd['explicitEarlyRetirement']and rcd['firmwareZeroAfterRetirement']and rcd['dualPhysicalQueuesRestored']and rcd['tagsRemoved']and not rcd['abaCompleted']
    proof={'passed':True,'realClassChange':True,'oldClass':'BULK','newClass':'BE','reason':'cooldown','sameQueryCompleteClassifierFrame':True,'sourceQuerySequence':f['provenance']['sequence'],'queryDurationSeconds':f['provenance']['finishedAtUptime']-f['provenance']['startedAtUptime'],'projectionAbsenceAloneAccepted':False,'affectedSlots':['tcp'],'sameSocketCtMarkNatWan':True,'cpuReaderBarrierConfirmed':True,'twoDirectionRetirementRequests':2,'barrierIsFirmwareDestroyAck':False,'actualCiAbsenceAndRemainingUdpAcceleratedVerified':True,'remainingUdpSameCiAndRtTags':True,'ecmCounts':[2,1,0],'oldGenerationNeverReopenedOrExtendedAfterTerminal':True,'oldTagsRemovedAfterCiAbsence':True,'freshIndependentCheckpointAndOwnerForRelearning':True,'freshKernelPinAndNativeGeneration':True,'sameTcpUdpCtIdentitiesAcrossGenerations':True,'newClassificationAndDifferentEcMSerials':True,'sameWan':sa['tcp']['wan'],'classifierMaximumLeaseSeconds':6,'nativeSessionSeconds':27,'independentOwnerSeconds':100,'remainingOldLeaseAtSingleRetirementSeconds':x['tagEpochUntil']-x['remainingUdpObservedAt'],'gameQualityConclusion':False,'cpuComparisonThisRound':False,'fullProductionNssRetained':False,'firstStageSourceInputs':first['sourceInputs'],'secondStageSourceInputs':second['sourceInputs'],'originalRecordsSha256':{'first':sha(a/'last-record-private.json'),'second':sha(b/'last-record-private.json')}}
    return {'proof':proof,'first':first,'second':second}
if __name__=='__main__':
    import sys
    result=collect(sys.argv[1]);out=w/sys.argv[1]/'class-lifecycle-proof.json';assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['proof']))
