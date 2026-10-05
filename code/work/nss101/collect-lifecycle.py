"""Sanitized lifecycle proof; preserve original private records and inputs."""
import hashlib,json,re,sys
from pathlib import Path
w=Path(__file__).resolve().parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def counters(raw):
 out={}
 for x in raw.get('nftables',[]):
  r=x.get('rule',{})
  for e in r.get('expr',[]):
   if 'counter'in e:out[r['comment'].split(':')[-1]]=e['counter']
 return out
def leaf(text):
 out={}
 for block in re.split(r'(?=^qdisc )',text,flags=re.M):
  h=re.match(r'qdisc \S+ (\S+)',block);m=re.search(r'backlog (\S+) (\d+)p',block);x=re.search(r'drop_overlimit (\d+).*?ecn_mark (\d+)',block)
  if h:out[h[1]]={'backlogRaw':m[1]if m else None,'backlogPackets':int(m[2])if m else None,'dropOverlimit':int(x[1])if x else None,'ecnMark':int(x[2])if x else None}
 return out
def stage(rel):
 p=w/rel;s=load(p/'last-record-private.json');result=load(p/'result.json');cp=load(p/'stage-checkpoint-verified.json');receipt=load(p/'stage-receipt-private.json');detached=load(p/'stage-detached-private.json');undo=load(p/'stage-undo-verified.json');base=load(p/'baseline-audit.json');before=load(p.parent/(p.name+'-before-audit.json'));after=load(p.parent/(p.name+'-after-audit.json'));inputs=load(p/'source-manifest.json')
 assert cp['gzipVerified']and receipt['success']and receipt['rollbackBeforeFirstWrite']and receipt['pipeInodesVerified']and receipt['parentIdentityVerified']and detached['identity']['ppid']==1
 assert all(undo.values())and base['configurationMatches']and all(base['checks'].values())and before['passed']and after['passed']
 assert all(sha((w/f).read_bytes())==digest and sha((p/'frozen'/f).read_bytes())==digest for f,digest in inputs.items())
 t={'caseLocalPath':rel,'passed':result['passed'],'sourceInputs':len(inputs),'sourceInputsCurrentAndFrozenMatch':True,'sourceManifestSha256':sha((p/'source-manifest.json').read_bytes()),'checkpointDownloadedShaAndGzipVerified':True,'guardianVerifiedBeforeFirstWrite':True,'guardianPpid':1,'independentOwnerSeconds':100,'fixedNativeSessionSeconds':27,'classifierMaximumLeaseSeconds':6,'ecmOpened':'frontendOpenedAt'in s,'completeABA':result['matchedForwardingABACompleted'],'phases':[{k:v[k]for k in ['name','seconds','completed','sampleCount']if k in v}for v in s.get('phases',[])],'renewals':len(s.get('renewals',[])),'rollback':undo,'baseline':base,'beforeFullAudit':before,'afterFullAudit':after,'softwareTagCounters':{k:counters(v)for k,v in s.items()if isinstance(v,dict)and'nftables'in v and'tcp_post_up_total'in counters(v)},'actualAcceleratedIdentity':load(p/'actual-accelerated-state-proof.json')if (p/'actual-accelerated-state-proof.json').exists()else None,'originalRecordSha256':sha((p/'last-record-private.json').read_bytes()),'originalResultSha256':sha((p/'result.json').read_bytes()),'error':s.get('error'),'gameQualityConclusion':False}
 if t['completeABA']:
  a=leaf(s['qosAccelerated']['qdisc']);b=leaf(s['qosAfterRetirement']['qdisc']);dt=s['qosAfterRetirement']['uptime']-s['qosAccelerated']['uptime'];m=load(p/'actual-long-metrics.json')
  t['metrics']=m;t['nativeQueueOptions']=s['qosReady']['validation'];t['nearBStatsSeconds']=dt;t['leafAdditionalStats']={k:{'beforeBacklogRaw':a[k]['backlogRaw'],'beforeBacklogPackets':a[k]['backlogPackets'],'afterBacklogRaw':b[k]['backlogRaw'],'afterBacklogPackets':b[k]['backlogPackets'],'dropOverlimitDelta':b[k]['dropOverlimit']-a[k]['dropOverlimit'],'ecnMarkDelta':b[k]['ecnMark']-a[k]['ecnMark']}for k in ['8f05:','8f06:']}
  t['leafSentPlusConfigured38ByteOverheadAccountingMbps']=sum(v['delta']['bytes']+38*v['delta']['packets']for v in m['leafAcrossBNearbySnapshots'].values())*8/dt/1e6
  t['asyncRateEstimateIsNotExactInstantaneousCap']=True;t['nativeSessionUsedSeconds']=s['frontendClosedAt']-s['frontendOpenedAt'];t['nativeSessionRemainingAtRetirementSeconds']=s['hardSessionUntilMs']/1000-s['frontendClosedAt'];t['queueBacklogParserRawUnitsRetained']=True
 return t
def closure(rel):
 p=w/rel;fw=json.loads(load(p/'firewall-after-private.json')['stdout']);server=load(p/'server-closed-private.json');guard=load(p/'guard-result-private.json');receipt=load(p/'firewall-receipt-private.json');detached=load(p/'firewall-detached-private.json');checkpoint=load(p/'firewall-checkpoint-verified.json');client=load(p/'result-private.json')
 assert fw['ownedRulesRemaining']==0 and fw['baselineRestored']and server['code']==0 and'MainPID=0'in server['stdout']and'ActiveState=inactive'in server['stdout']and'LISTEN'not in server['stdout']and'UNCONN'not in server['stdout']
 assert guard['passed']and guard['exactClientOnly']and guard['clientExitedBeforeDeadline']and receipt['beforeWriteIndependentGuardianVerified']and detached['detachedIdentityVerified']and detached['onlyNullStandardFds']and checkpoint['expirySeconds']==180
 return {'loadLocalPath':rel,'temporaryFirewallRulesRemaining':0,'canonicalFirewallBaselineRestored':True,'ownedUnitInactiveMainPidZeroPortsClosed':True,'clientExited':True,'clientGuardPassed':True,'independentFirewallExpirySeconds':180,'independentClientDeadlineSeconds':210,'endpointGuardianVerifiedBeforeWrite':True,'clientRunSeconds':client['seconds'],'clientErrors':[re.sub(r'(?:\d{1,3}\.){3}\d{1,3}','[address]',x)for x in client.get('errors',[])]}
if __name__=='__main__':
 p=w/sys.argv[1];x=stage(sys.argv[1]);out=p/'sanitized-lifecycle.json';assert not out.exists();out.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({'passed':x['passed'],'sourceInputs':x['sourceInputs'],'phases':len(x['phases']),'renewals':x['renewals'],'rollbackVerified':True}))
