-- Pure six-account config construction. Queue/filter captures must be taken
-- after complete old-owner recovery, with the candidate source still stopped.
local M={}
local function copy(v)if type(v)~='table'then return v end;local t={};for k,x in pairs(v)do t[k]=copy(x)end;return t end
function M.prepare(old,capture,hashes,generation)
 assert(old.version==23 and (old.wanCount or 5)==5,'Expected installed five-account source')
 assert(type(generation)=='string' and generation:match('^nss23%-wan6%-%w[%w%-]*$'))
 assert(capture.oldOwnerRecovered and capture.nativeStopped and capture.noDynamicSelectors,'Complete owner recovery required')
 assert(capture.ramOwnerRetired and capture.ramJournalEmpty,'Old RAM journal cannot change account topology in place')
 assert(type(capture.boot)=='string' and type(capture.transaction)=='string')
 local cfg=copy(old);cfg.wanCount=6;cfg.policy.wanCount=6;cfg.generation=generation
 cfg.installTransaction=capture.transaction;cfg.adoptionBoot=capture.boot
 cfg.source.groupRunnerPath='/root/router-project/classifier/'..generation..'/group-runner'
 cfg.queues={};cfg.originalNative={};cfg.priorRules={};cfg.files={}
 for w=1,6 do for _,prefix in ipairs{'rpwan','rpifb'}do
  local dev=prefix..w;local q=assert(capture.queues[dev]);local native=assert(capture.native[dev])
  assert(q.root and q.kind=='cake' and q.handle:match('^%x+:$'))
  assert(q.options and q.options.bandwidth>0 and q.options.diffserv=='diffserv4')
  if w<=5 then
   local previous=assert(old.queues[dev]);assert(q.handle==previous.handle,'Existing queue handle changed')
   local a,b=copy(q.options),copy(previous.options);a.bandwidth=nil;b.bandwidth=nil
   for k,v in pairs(a)do assert(b[k]==v,'Existing queue options changed')end
   for k,v in pairs(b)do assert(a[k]==v,'Existing queue options lost')end
  else assert(q.options.flowmode==(prefix=='rpwan' and 'dual-srchost' or 'dual-dsthost') and q.options.nat==true)end
  assert(type(native)=='string' and not native:find('pref 410%d%d') and not native:find('pref 411%d%d'),'Dynamic selectors remain')
  cfg.queues[dev]={handle=q.handle,options=copy(q.options)};cfg.originalNative[dev]=native;cfg.priorRules[dev]={}
 end end
 for name,hash in pairs(hashes)do
  assert(name:match('^[a-z0-9%.%-]+$') and not name:find('..',1,true) and hash:match('^[a-f0-9]+$') and #hash==64)
  cfg.files[name]=hash
 end
 for _,name in ipairs{'worker.lua','guardian.lua','backend.lua','owned.lua','classifier-core.lua','conntrack-source.lua','stop-worker.lua','cleanup.sh','init.sh','group-runner','process-stop','process-crash'}do assert(cfg.files[name],'Missing pinned source/helper')end
 return cfg
end
return M
