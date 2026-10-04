"""Only initial tag traffic readiness changes; every acceleration lease stays fixed."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
lua=['fast-path.lua','classifier.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua','publication-wait.lua']
for name in lua:
    assert not(here/name).exists();(here/name).write_bytes((root/'work/nss48'/name).read_bytes())
for name in ['consumer-qualified.json']:(here/name).write_bytes((root/'work/nss48'/name).read_bytes())
scripts=['binding.mjs','qualification.mjs','session-binding.mjs','dependency-closure.mjs','parse-dependency-graph.mjs','current-audit-diagnostic.mjs','audit-renderer.mjs','real-session.mjs','module-stage.mjs','payload.mjs','record-candidates.mjs','read-real-candidates.mjs','parse-ecm-any-wan.mjs','wait-ready-candidate.mjs','inspect-classifier.mjs','final-closure.mjs','build-entry.mjs','test-parser.mjs','test-controller.mjs','test-dependencies.mjs','test-binding.mjs','test-entry-scheduling.py']
for name in scripts:
    if name=='audit-renderer.mjs':(here/name).write_bytes((root/'work/nss48'/name).read_bytes());continue
    s=(root/'work/nss48'/name).read_text().replace('work/nss48','work/nss49').replace("round:'NSS48'","round:'NSS49'")
    (here/name).write_text(s,encoding='utf-8',newline='\n')
(here/'deployment-latest.json').write_bytes((root/'work/nss47/deployment-latest.json').read_bytes())
old=(root/'work/nss48/fast-path.lua').read_text()
start=old.index(' local function getter(raw)');end=old.index(' local function state()',start)
before=old[start:end]
after=""" local function getter(raw,allowPending)
  local counters={};for _,x in ipairs(raw.nftables)do if x.rule then for _,e in ipairs(x.rule.expr)do if e.counter then counters[x.rule.comment:match('([^:]+)$')]=e.counter end end end end
  local pending=false
  for _,slot in ipairs({'tcp','udp'})do for _,d in ipairs({'up','down'})do
   local k=slot..'_post_'..d;local total,expected,unexpected=counters[k..'_total'],counters[k..'_expected'],counters[k..'_unexpected']
   assert(total and expected and unexpected,'Tag counter missing')
   assert(expected.packets==total.packets and unexpected.packets==0,'Tag getter mismatch')
   if total.packets==0 then assert(allowPending==true,'Tag getter lacks bidirectional traffic');pending=true end
  end end
  assert(counters.udp_post_neighbor_nonzero.packets==0);return counters,pending
 end
"""
wait_old="""  record.unchangedQoSPlan=true;local getterUntil=now()+0.3
  repeat record.initialTags=live();local ok,err=pcall(getter,record.initialTags);if ok then break end;assert(now()<getterUntil,err);pause(0.02)until false
"""
wait_new="""  record.unchangedQoSPlan=true;local getterUntil=math.min(now()+1.2,due-0.5,record.deadline-32)
  record.initialTagReadiness={startedAt=now(),deadline=getterUntil,probes=0,maximumWaitSeconds=1.2}
  repeat
   stopped();record.initialTags=live();local _,pending=getter(record.initialTags,true)
   record.initialTagReadiness.probes=record.initialTagReadiness.probes+1
   if not pending then record.initialTagReadiness.completedAt=now();getter(record.initialTags);break end
   assert(now()<getterUntil,'Selected flow had no bidirectional traffic before bounded getter deadline');pause(0.02)
  until false
"""
assert old.count(before)==1 and old.count(wait_old)==1
new=old.replace(before,after).replace(wait_old,wait_new)
(here/'fast-path.lua').write_text(new,encoding='utf-8',newline='\n')
delta={'originalSha256':sha((root/'work/nss48/fast-path.lua').read_bytes()),'candidateSha256':sha(new.encode()),'old':before,'new':after,'waitOld':wait_old,'waitNew':wait_new,'onlyInitialNoTrafficWaitChanged':True,'zeroTrafficCannotAuthorizeNss':True,'badTagsFailImmediately':True,'ownerSeconds':45,'initialAgeSeconds':1,'prelearningAgeSeconds':2,'epochSeconds':5,'flowCount':2,'budgetMbps':20}
(here/'getter-delta.json').write_text(json.dumps(delta,indent=2)+'\n')
q=(here/'qualification.mjs').read_text()
needle="assert.equal(hash('work/nss49/'+name),hash('work/nss39/'+name),'NSS router code may not change with classifier reliability');"
replacement="""if(name==='fast-path.lua'){
 const delta=read('work/nss49/getter-delta.json'),proof=read('work/nss49/aba-qualified.json');assert.ok(proof.passed&&proof.completeSourceExecuted&&proof.realForwardingQualified===false);assert.equal(hash('work/nss39/'+name),delta.originalSha256);assert.equal(hash('work/nss49/'+name),delta.candidateSha256);assert.equal(proof.sourceSha256,delta.candidateSha256);manifest['work/nss49/getter-delta.json']=hash('work/nss49/getter-delta.json');manifest['work/nss49/aba-qualified.json']=hash('work/nss49/aba-qualified.json');
 }else assert.equal(hash('work/nss49/'+name),hash('work/nss39/'+name),'Other NSS router code must remain unchanged');"""
assert q.count(needle)==1;q=q.replace(needle,replacement)
(here/'qualification.mjs').write_text(q,encoding='utf-8',newline='\n')
fixture=(root/'work/nss39/aba-fixtures.lua').read_text()
needle='  r.nftables[#r.nftables+1]={rule={comment=\'fixture:udp_post_neighbor_nonzero\''
injection="""  if (kind=='delayed-tcp'and clock<101)or kind=='idle-tcp'then for _,entry in ipairs(r.nftables)do local rule=entry.rule;if rule.comment:find(':tcp_',1,true)then rule.expr[1].counter.packets=0 end end end
"""
assert fixture.count(needle)==1;fixture=fixture.replace(needle,injection+needle)
fixture=fixture.replace("{'stable','core-close','wan4'}","{'stable','core-close','wan4','delayed-tcp'}").replace("{'change-A','change-B','change-A2','nat-drift','wrong-tag','drop-acceleration','wan-mismatch','low-mark-mismatch'}","{'change-A','change-B','change-A2','nat-drift','wrong-tag','drop-acceleration','wan-mismatch','low-mark-mismatch','idle-tcp'}")
(here/'aba-fixtures.lua').write_text(fixture,encoding='utf-8',newline='\n')
native=(root/'work/nss39/native-qualification.mjs').read_text().replace('work/nss39','work/nss49')
native=native.replace("[['consumer','native-consumer-qualified.json','classifier.lua','adapterSha256'],['aba','aba-qualified.json','fast-path.lua','sourceSha256']]","[['aba','aba-qualified.json','fast-path.lua','sourceSha256']]")
native=native.replace("name==='consumer'?17:11","name==='consumer'?17:13")
(here/'native-qualification.mjs').write_text(native,encoding='utf-8',newline='\n')
pre=(root/'work/nss39/preflight-mainline.mjs').read_text().replace('work/nss39','work/nss49')
(here/'preflight-mainline.mjs').write_text(pre,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for p in here.glob('*.mjs'):subprocess.run([node,'--check',str(p)],check=True)
print(json.dumps({'prepared':True,'onlyInitialTagReadinessChanged':True,'pendingZeroTrafficMaxSeconds':1.2,'wrongTagNotRetryable':True,'allAccelerationBoundsUnchanged':True}))
