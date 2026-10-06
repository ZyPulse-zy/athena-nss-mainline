local cases={}
for _,kind in ipairs({'same-query','new-complete-query','old-complete-query','producer-drift','projection-instead-of-full','missing-udp','stale-source','invalid-full-source','recovered-class','invalid-json'})do
 local at=10;local P={selected={tcp={classifierKey='tcp-model'},udp={classifierKey='udp-model'}}};local epoch={};local record={};local ram='model-only';local context={model=true}
 local probe={producer='p',generation='g',boot='b',configSha256='h',pid=1,start='s',snapshot={provenance={sequence=100},admissionProjection=true}}
 local full={producer='p',generation='g',boot='b',configSha256='h',pid=1,start='s',sourceValid=true,at=10,class='BE',snapshot={provenance={sequence=kind=='same-query'and 100 or kind=='old-complete-query'and 99 or 101},flows={{key='tcp-model'},{key='udp-model'}}}}
 if kind=='producer-drift'then full.producer='changed'end
 if kind=='projection-instead-of-full'then full.snapshot.admissionProjection=true end
 if kind=='missing-udp'then full.snapshot.flows[2]=nil end
 if kind=='stale-source'then full.at=3 end
 if kind=='invalid-full-source'then full.sourceValid=false end
 if kind=='recovered-class'then full.class='BULK'end
 local function now()return at end
 local reads=0;local function stable(path,limit)assert(path=='model-only/snapshot.json'and limit==4194304);reads=reads+1;return kind=='invalid-json'and'not-json'or j.stringify(full)end
 local Consumer={inspect=function(x,c,t)assert(c==context and x.sourceValid and t-x.at<6);return{}end,compareEpoch=function(_,x)
  if x.snapshot.admissionProjection or x.class=='BE'then return{action='RETIRE_EXACT_SELECTED_SLOTS',affected={'tcp'}}end
  return{action='KEEP_IMMUTABLE_EPOCH'}
 end}
 local function describeSelection(x,_,t)return{sameAdmissionFrame=true,sourceSequence=x.snapshot.provenance.sequence,slots={tcp={class=x.class},udp={class='RT'}},checkedAtUptime=t,nssAdmissionAllowed=false}end
 local out={lastObservedSnapshot=probe,lastObservedContext=context};local function diagnose()error('Active path must not reuse projection diagnosis')end
 __COMPLETE_CURRENT_AND_COMPARE__
 local result=out.compareObserved(false);assert(reads==1,'More than one full read')
 if kind=='same-query'or kind=='new-complete-query'then
  local f=assert(result.evidence.completeSelected);assert(f.sameSourceCompleteFrame and f.afterRejectionOnly and f.comparisonMadeFromThisCompleteQuery and f.projectionRejectionSequence==100)
  assert(f.sourceSequence==(kind=='same-query'and 100 or 101));assert(result.action=='RETIRE_EXACT_SELECTED_SLOTS'and #result.affected==1 and result.affected[1]=='tcp')
 else assert(not result.evidence.completeSelected and type(result.evidence.completeSelectionUnavailable)=='string');assert(result.action=='RETIRE_EXACT_SELECTED_SLOTS')end
 cases[#cases+1]={case=kind,passed=true,actualNewReaderAndComparisonExecuted=true,consumerAndBackendMocked=true,hardwareProof=false}
end
print(j.stringify({passed=true,checks=#cases,cases=cases,exactlyOneCompleteReadAfterProjectionRejection=true,comparisonFromSingleCompleteQuery=true,fullFactoryModeled=false,productionWrites=false}))
