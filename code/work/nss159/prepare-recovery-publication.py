"""Preserve two read-only closure refusals and require exact natural recovery."""
from pathlib import Path
p=Path(__file__).resolve().parent/'export-evening.py';s=p.read_text(encoding='utf-8')
assert s.count("v1-final-health.json")==1;s=s.replace('v1-final-health.json','v3-final-health.json')
s=s.replace("assert all(x['passed'] for x in [health,physical,end,recv,down])","recovery=read(even/'v3-wan4-recovery-proof.json')\nassert recovery['passed'] and recovery['tenRecoveryRampStepsReproduced'] and recovery['onlyThreeWan4DhcpRulesRestored']\nassert health['wan4Up'] and health['wan4Ipv4Present'] and health['allFiveWanHealthy'] and health['exactWan4AutomaticRecoveryProved']\nassert (even/'v1-final-failure-private.json').exists() and (even/'v2-final-failure-private.json').exists()\nassert all(x['passed'] for x in [health,physical,end,recv,down])")
old="'originalSourcesAndFailurePreserved':True}]\nfirst=r/"
new="'originalSourcesAndFailurePreserved':True},\n {'case':'evening-four-wan-assertion','reason':'WAN4 naturally recovered; the old rigid four-WAN audit refused read-only closure. Original failure retained; unchanged-controller ten-step exact 300-bucket recovery replay verified','routerNssWrites':False,'originalSourcesAndFailurePreserved':True},\n {'case':'evening-dhcp-model-v1','reason':'First recovery model assumed subnet normalization and original insertion order; actual DHCP rule contains host/prefix and is appended among equal priorities. Exact removal leaves previous four-WAN rules byte-identical; corrected strict lease-derived three-rule model passed','routerNssWrites':False,'originalSourcesAndFailurePreserved':True}]\nfirst=r/"
assert s.count(old)==1;s=s.replace(old,new)
assert s.count('WAN4仍既有认证down/四路failover，未主动认证。')==1
s=s.replace('WAN4仍既有认证down/四路failover，未主动认证。','WAN4自然恢复：原控制器十步恢复权重和全部300桶精确重现，五路各60桶；仅恢复三条由实际DHCP租约派生的WAN4规则。旧四路断言拒绝及首个DHCP模型错误均保留，未主动认证或修改路由。')
s=s.replace("'evening-final-audit':health,","'evening-final-audit':health,'wan4-natural-recovery':recovery,")
p.write_text(s,encoding='utf-8')
p=p.with_name('update-checker.py');s=p.read_text(encoding='utf-8')
s=s.replace("len(load159('failures'))==5","len(load159('failures'))==7")
s=s.replace("and not rt159['audit']['wan4Up']","and rt159['audit']['wan4Up'] and rt159['audit']['wan4Ipv4Present'] and rt159['audit']['allFiveWanHealthy']")
s=s.replace("'exactWan4AutomaticFailoverProved'","'exactWan4AutomaticRecoveryProved'")
s=s.replace("assert manifest['lastAppendExport']=='NSS159'","recovery159=load159('wan4-natural-recovery');assert recovery159['passed'] and recovery159['unchangedProtectedHealthControllerSource'] and recovery159['tenRecoveryRampStepsReproduced'] and recovery159['exact300BucketSourceAlgorithmReproduced']\nassert recovery159['priorBucketCounts']==[75,75,75,0,75] and recovery159['newBucketCounts']==[60,60,60,60,60]\nassert recovery159['onlyThreeWan4DhcpRulesRestored'] and recovery159['wan4RulesDerivedFromActualLease'] and not recovery159['experimentRoutingMutation'] and not recovery159['nssPermissionGranted']\nassert manifest['lastAppendExport']=='NSS159'")
p.write_text(s,encoding='utf-8')
print('Natural recovery required; two original closure refusals preserved')
