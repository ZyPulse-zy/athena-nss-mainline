-- Pure, anonymous reducers. Counter sources and units are never merged.
local M={}
local MAX_INTEGER=9007199254740991
function M.number(s)
 local n=tonumber(s);if n and n==n and n>=0 and n%1==0 and n<=MAX_INTEGER then return n end
end
local function trim(s)return(s:gsub('^%s+',''):gsub('%s+$',''))end
function M.query_state(code,text,truncated)
 if truncated then return 'oversize' end
 if code==124 or code==137 or code==143 then return 'timeout' end
 if code==0 then return 'ok' end
 text=(text or''):lower()
 if text:find('not supported',1,true) or text:find('(-95)',1,true) then return 'unsupported' end
 if text:find('not found',1,true) or text:find('no such file',1,true) then return 'missing' end
 return 'failed'
end
function M.interfaces(text)
 local rows,phy,current={},nil,nil
 for line in(text or''):gmatch('[^\n]+')do
  local p=line:match('^phy#(%d+)');if p then phy='phy'..p end
  local name=line:match('^%s+Interface ([%w_.%-]+)%s*$')
  if name and phy then current={name=name,phy=phy};rows[#rows+1]=current end
  if current then
   current.ifindex=tonumber(line:match('^%s+ifindex (%d+)'))or current.ifindex
   current.wdev=line:match('^%s+wdev (%S+)')or current.wdev
   current.address=line:match('^%s+addr ([%x:]+)')or current.address
   current.kind=line:match('^%s+type (.+)')or current.kind
   local ch,freq,width=line:match('channel (%d+) %((%d+) MHz%), width: (%d+) MHz')
   if ch then current.channel=tonumber(ch);current.frequencyMHz=tonumber(freq);current.widthMHz=tonumber(width)end
   current.center1MHz=tonumber(line:match('center1: (%d+) MHz'))or current.center1MHz
   current.center2MHz=tonumber(line:match('center2: (%d+) MHz'))or current.center2MHz
   current.txpowerDbm=tonumber(line:match('txpower ([%d.%-]+) dBm'))or current.txpowerDbm
  end
 end
 table.sort(rows,function(a,b)return a.name<b.name end);return rows
end
function M.regions(text)
 local out,scope={},'global'
 for line in(text or''):gmatch('[^\n]+')do
  if line:match('^global')then scope='global'end
  local p=line:match('^phy#(%d+)');if p then scope='phy'..p end
  local country=line:match('country ([A-Z0-9][A-Z0-9]):')
  if country then out[scope]=country end
 end
 return out
end
local station_fields={['tx bytes']='txBytes',['rx bytes']='rxBytes',['tx packets']='txPackets',
 ['rx packets']='rxPackets',['tx retries']='txRetries',['tx failed']='txFailed',
 ['tx duration']='txDurationUs',['rx duration']='rxDurationUs'}
M.station_fields=station_fields
function M.stations(text)
 local rows,current,tid={},nil,nil
 for line in(text or''):gmatch('[^\n]+')do
  local mac,ap=line:match('^Station ([%x:]+) %(on ([%w_.%-]+)%)')
  if mac then current={mac=mac:lower(),ap=ap,counters={},tids={}};rows[#rows+1]=current;tid=nil end
  if current then
   local id=line:lower():match('^%s+tid%s+(%d+)%s*:?%s*$')
   if id then tid=tonumber(id);current.tids[tid]={} end
   local k,v=line:match('^%s+([^:]+):%s*(.-)%s*$')
   if k then
    k=trim(k):lower();local counter=station_fields[k]
    if counter then current.counters[counter]=M.number(v:match('^(%d+)'))end
    if k=='connected time'then current.connectedSeconds=M.number(v:match('^(%d+)'))end
    if k=='inactive time'then current.inactiveMs=M.number(v:match('^(%d+)'))end
    if k=='signal'or k=='signal avg'then current[k=='signal'and'signalDbm'or'signalAvgDbm']=tonumber(v:match('^([%d%-]+)'))end
    if k=='tx bitrate'or k=='rx bitrate'then current[k=='tx bitrate'and'txRateMbps'or'rxRateMbps']=tonumber(v:match('^([%d.]+)'))end
    if k=='authorized'or k=='authenticated'or k=='associated'then if v=='yes'then current[k]=true elseif v=='no'then current[k]=false end end
    local tid_fields={['rx msdu']='rxMsdu',['tx msdu']='txMsdu',['tx msdu retries']='txMsduRetries',['tx msdu failed']='txMsduFailed'}
    if tid and tid_fields[k] then current.tids[tid][tid_fields[k]]=M.number(v:match('^(%d+)'))end
   end
  end
 end
 return rows
end
function M.survey(text)
 local out,current={},nil
 for line in(text or''):gmatch('[^\n]+')do
  local freq=line:match('frequency:%s*(%d+) MHz')
  if freq then current={frequencyMHz=tonumber(freq),inUse=line:find('[in use]',1,true)~=nil};out[current.frequencyMHz]=current end
  if current then
   local k,v=line:match('channel%s+([%w ]+)time:%s*(%d+) ms')
   if k then k=trim(k);local key=({active='activeMs',busy='busyMs',receive='receiveMs',transmit='transmitMs'})[k];if key then current[key]=M.number(v)end end
   current.noiseDbm=tonumber(line:match('noise:%s*([%d%-]+) dBm'))or current.noiseDbm
  end
 end
 return out
end
function M.peer(text)
 local out={};for k,v in(text or''):gmatch('([%w_]+)%s+(%d+)')do
  if({tx_packets=true,tx_bytes=true,tx_retries=true,tx_failed=true,rx_packets=true,rx_bytes=true,rx_dropped=true,rx_retries=true,
   tx_failed_retries=true,tx_multiple_retries=true,tx_mpdu_retries=true,tx_mpdu_total_retries=true})[k]then out[k]=M.number(v)end
 end;return out
end
function M.airtime(text)
 local out={txUs=M.number((text or''):match('TX:%s*(%d+) us')),rxUs=M.number((text or''):match('RX:%s*(%d+) us')),deficitUs={}}
 for ac,v in(text or''):gmatch('([A-Z][A-Z]):%s*([%d%-]+) us')do if ac=='VO'or ac=='VI'or ac=='BE'or ac=='BK'then out.deficitUs[ac]=tonumber(v)end end
 return out
end
-- mac80211 debugfs airtime/aqm tables: retain typed numeric rows, never names.
-- These are host scheduler observations, not final firmware TID/AC readback.
function M.table_stats(text)
 local rows={};local header
 for line in(text or''):gmatch('[^\n]+')do
  local clean=trim(line):lower()
  if clean:match('^ac%s+aql limit low')then header={'ac','limitLowUs','limitHighUs'}
  elseif clean:match('^ac%s+aql pending')then header={'ac','pendingUs'}
  elseif clean:match('^tid%s')or clean:match('^ac%s')then header={};for v in clean:gmatch('[%w_%-]+')do header[#header+1]=v end end
  if header then
   local cells={};for v in clean:gmatch('%S+')do cells[#cells+1]=v end
   local key=cells[1];if key and(key:match('^%d+$')or key=='vo'or key=='vi'or key=='be'or key=='bk')then
    local row={};for i,v in ipairs(cells)do
     local column=header[i]or('column'..i)
     if v=='vo'or v=='vi'or v=='be'or v=='bk'then row[column]=v:upper()else row[column]=tonumber(v)end
    end
    if type(row.ac)=='number'then row.acName=({[0]='VO',[1]='VI',[2]='BE',[3]='BK'})[row.ac]end
    rows[#rows+1]=row
   end
  end
 end
 return{state=#rows>0 and'ok'or(header and'empty'or'unparsed'),rows=rows}
end
function M.delta(a,b,sa,sb,epoch)
 if sa~='ok'then return{state=sa or'missing',endpoint='start'}end
 if sb~='ok'then return{state=sb or'missing',endpoint='end'}end
 if epoch~=true then return{state=type(epoch)=='string'and epoch or'epoch-changed'}end
 if a==nil or b==nil then return{state='missing'}end
 if b<a then return{state='reset'}end
 return{state='ok',value=b-a}
end
function M.same_radio(a,b)
 if not a or not b then return false end
 for _,k in ipairs{'phy','name','ifindex','wdev','address','kind','channel','frequencyMHz','widthMHz','center1MHz','center2MHz','txpowerDbm','country'}do
  if a[k]~=b[k]then return false end
 end
 return a.frequencyMHz~=nil and a.widthMHz~=nil and a.ifindex~=nil and a.wdev~=nil and a.address~=nil
end
function M.survey_delta(a,b,sa,sb,epoch)
 local out={scope='reported-frequency-not-entire-wide-channel',externalInterferenceMeasured=false}
 for _,k in ipairs{'activeMs','busyMs','receiveMs','transmitMs'}do out[k]=M.delta(a and a[k],b and b[k],sa,sb,epoch)end
 local active,busy=out.activeMs,out.busyMs
 if active.state=='ok'and busy.state=='ok'then
  if active.value==0 then out.busyFraction={state='no-exposure'}
  elseif busy.value>active.value then out.busyFraction={state='inconsistent'}
  else out.busyFraction={state='ok',value=busy.value/active.value}end
 else out.busyFraction={state=active.state~='ok'and active.state or busy.state}end
 return out
end
function M.aqm_delta(a,b,sa,sb,epoch)
 local rows,old={},{}
 for _,row in ipairs(M.table_stats(a).rows)do if row.tid~=nil and row.ac~=nil then old[tostring(row.tid)..'/'..tostring(row.ac)]=row end end
 for _,row in ipairs(M.table_stats(b).rows)do if row.tid~=nil and row.ac~=nil then
  local before=old[tostring(row.tid)..'/'..tostring(row.ac)];local item={tid=row.tid,ac=row.ac,acName=row.acName,counters={}}
  for _,k in ipairs{'drops','marks','overlimit','collisions','tx-bytes','tx-packets'}do
   item.counters[k]=M.delta(before and before[k],row[k],sa,sb,epoch)
  end
  rows[#rows+1]=item
 end end
 return rows
end
local function query(sample,key)return sample.queries[key]or{state='missing'}end
function M.report(first,last)
 local out={schema=1,readOnly=true,generatedTraffic=false,samples=2,queries={},aps={},radios={},stations={},
  endToEndLossMeasured=false,finalAirTidAcVerified=false,counterRatiosCalculated=false,
  elapsedSeconds=last.finished-first.started,requestedSeconds=first.requestedSeconds,
  limits=first.limits,notices={'AP tx is wireless downlink; AP rx is client uplink.',
  'Busy time includes own BSS activity and is not an external interference percentage.',
  'Counters from nl80211, mac80211 and NSS remain separate; zero is only a measured value.',
  'Rates are recent driver estimates, not delivered throughput or client uplink QoS.',
  'TX failed can include NSS TQM drops; it is not necessarily retry-exhaustion over the air.'}}
 for _,sample in ipairs{first,last}do
  for _,q in ipairs(sample.costs)do out.queries[#out.queries+1]={kind=q.kind,state=q.state,seconds=q.finished-q.started,exitCode=q.exitCode,endpoint=sample==first and'start'or'end'}end
 end
 local bootOk=first.boot and last.boot and first.boot==last.boot
 local byName={};for _,ap in ipairs(first.interfaces)do byName[ap.name]=ap end
 local apAliases,phyAliases,stationAliases={},{},{};local phyOrder={}
 for _,sample in ipairs{first,last}do for _,ap in ipairs(sample.interfaces)do
  if not apAliases[ap.name]then apAliases[ap.name]='ap'..(#out.aps+1);out.aps[#out.aps+1]={alias=apAliases[ap.name]}end
  if not phyAliases[ap.phy]then phyOrder[#phyOrder+1]=ap.phy;phyAliases[ap.phy]='radio'..#phyOrder end
 end end
 for _,ap in ipairs(last.interfaces)do
  local entry;for _,v in ipairs(out.aps)do if v.alias==apAliases[ap.name]then entry=v end end
  entry.radio=phyAliases[ap.phy];entry.mode=ap.kind
  for _,k in ipairs{'channel','frequencyMHz','widthMHz','center1MHz','center2MHz','txpowerDbm','country'}do
   local state=ap[k]~=nil and'ok'or'missing';if k=='country'and ap.regionState~='ok'then state=ap.regionState or'missing'end
   entry[k]={state=state,value=ap[k]}
  end
  entry.stable=bootOk and M.same_radio(byName[ap.name],ap)or false
  entry.stationQueries={start=query(first,'stations:'..ap.name).state,finish=query(last,'stations:'..ap.name).state}
 end
 for _,phy in ipairs(phyOrder)do
  local key='survey:'..phy;local aq,bq=query(first,key),query(last,key);local a,b=first.surveys[phy]or{},last.surveys[phy]or{}
  local radio={alias=phyAliases[phy],survey={},hostAql={}};out.radios[#out.radios+1]=radio
  local flags=query(last,'phy:'..phy..':hwflags');radio.hwFlags={state=flags.state,values={}}
  if flags.state=='ok'then local set={};for line in flags.text:gmatch('[^\n]+')do set[trim(line)]=true end
   for _,flag in ipairs{'HAS_TX_QUEUE','SUPPORTS_TID_CLASS_OFFLOAD','SUPPORTS_NSS_OFFLOAD','SUPPORTS_TX_ENCAP_OFFLOAD'}do
   radio.hwFlags.values[flag]=set[flag]or false
  end end
  local feature=query(last,'phy:'..phy..':features')
  radio.hostAql.featureAdvertisement={queryState=feature.state,api='nl80211-EXT_FEATURE_AQL',state=feature.state}
  if feature.state=='ok'then
   radio.hostAql.featureAdvertisement.state=feature.text:match('%[%s*AQL%s*%]')and'advertised'or'not-observed'
  end
  local representative=last.surveyInterfaces and last.surveyInterfaces[phy]
  local stable=bootOk and representative and first.surveyInterfaces and first.surveyInterfaces[phy]==representative
  local current;for _,ap in ipairs(last.interfaces)do if ap.name==representative then current=ap end end
  stable=stable and M.same_radio(byName[representative],current)or false
  for freq,v in pairs(b)do if v.inUse then
   local old=a[freq];radio.survey[#radio.survey+1]={frequencyMHz=freq,noiseDbm=v.noiseDbm,
    intervalSeconds=bq.finished and aq.finished and bq.finished-aq.finished or nil,
    counters=M.survey_delta(old,v,aq.state,bq.state,stable and old and old.inUse)}
  end end
  radio.surveyState=aq.state~='ok'and aq.state or bq.state
  if radio.surveyState=='ok'and #radio.survey==0 then radio.surveyState='missing'end
  for _,name in ipairs{'aql_enable','aql_pending','aql_txq_limit'}do
   local q=query(last,'phy:'..phy..':'..name);radio.hostAql[name]={state=q.state}
   if q.state=='ok'then
    if name=='aql_enable'then radio.hostAql[name].value=tonumber(trim(q.text))else radio.hostAql[name].statistics=M.table_stats(q.text)end
   end
  end
 end
 local oldStations={};for _,s in ipairs(first.stations)do oldStations[s.ap..'/'..s.mac]=s end
 local count=0;for _,sample in ipairs{first,last}do for _,s in ipairs(sample.stations)do if not stationAliases[s.mac]then count=count+1;stationAliases[s.mac]='station'..count end end end
 for _,s in ipairs(last.stations)do
  local key=s.ap..'/'..s.mac;local old=oldStations[key];local a=query(first,'stations:'..s.ap);local b=query(last,'stations:'..s.ap)
  local ap;for _,v in ipairs(last.interfaces)do if v.name==s.ap then ap=v end end
  local epoch=true
  if not bootOk or not M.same_radio(byName[s.ap],ap)then epoch='epoch-changed'
  elseif not old then epoch='association-unobserved'
  elseif not old.connectedSeconds or not s.connectedSeconds then epoch='epoch-unverified'
  elseif s.connectedSeconds<old.connectedSeconds then epoch='association-reset'
  elseif not a.finished or not b.finished then epoch='epoch-unverified'
  elseif math.abs((s.connectedSeconds-old.connectedSeconds)-(b.finished-a.finished))>2 then epoch='association-discontinuous'end
  local row={alias=stationAliases[s.mac],ap=apAliases[s.ap],associationObserved=true,
   authorized=s.authorized,authenticated=s.authenticated,associated=s.associated,
   signalDbm=s.signalDbm,signalAvgDbm=s.signalAvgDbm,txRateMbps=s.txRateMbps,rxRateMbps=s.rxRateMbps,
   inactiveMs=s.inactiveMs,intervalSeconds=b.finished and a.finished and b.finished-a.finished or nil,
   counters={},tids={},debug={},sameAssociation=epoch==true,counterBasis='nl80211-driver-export-dependent'}
  for _,k in pairs(station_fields)do row.counters[k]=M.delta(old and old.counters[k],s.counters[k],a.state,b.state,epoch)end
  for id,stats in pairs(s.tids)do
   local tid={tid=id,counters={}};row.tids[#row.tids+1]=tid
   for _,k in ipairs{'txMsdu','rxMsdu','txMsduRetries','txMsduFailed'}do tid.counters[k]=M.delta(old and old.tids[id]and old.tids[id][k],stats[k],a.state,b.state,epoch)end
  end
  row.tidState=#row.tids>0 and'ok'or'not-exported'
  for _,name in ipairs{'nss_stats','airtime','aqm','aql','tx_retry_count','tx_retry_failed'}do
   local da=query(first,'sta:'..key..':'..name);local db=query(last,'sta:'..key..':'..name)
   local item={state=db.state,scope=name=='nss_stats'and'NSS-peer-export-separate-basis'or'mac80211-host-statistics'};row.debug[name]=item
   if db.state=='ok'then
    if name=='nss_stats'then item.counters={};local pa,pb=M.peer(da.text),M.peer(db.text)
     for _,k in ipairs{'tx_packets','tx_bytes','tx_retries','tx_failed','rx_packets','rx_bytes','rx_dropped','rx_retries',
      'tx_failed_retries','tx_multiple_retries','tx_mpdu_retries','tx_mpdu_total_retries'}do item.counters[k]=M.delta(pa[k],pb[k],da.state,db.state,epoch)end
     item.semanticStatus='firmware-layout-and-counter-basis-require-source-audit'
    elseif name=='airtime'then
     local pa,pb=M.airtime(da.text),M.airtime(db.text);item.counters={}
     for _,k in ipairs{'txUs','rxUs'}do item.counters[k]=M.delta(pa[k],pb[k],da.state,db.state,epoch)end
     item.deficitUs=pb.deficitUs
    elseif name=='tx_retry_count'or name=='tx_retry_failed'then item.counter=M.delta(M.number(trim(da.text or'')),M.number(trim(db.text)),da.state,db.state,epoch)
    else item.statistics=M.table_stats(db.text);item.statisticsBasis='host-scheduler-endpoint-snapshot'
     if name=='aqm'then item.counterDeltas=M.aqm_delta(da.text,db.text,da.state,db.state,epoch)end
    end
   end
  end
  out.stations[#out.stations+1]=row;oldStations[key]=nil
 end
 out.departedStations=0;out.unobservedStations=0
 for _,s in pairs(oldStations)do
  if query(last,'stations:'..s.ap).state=='ok'then out.departedStations=out.departedStations+1
  else out.unobservedStations=out.unobservedStations+1 end
 end
 out.topology={start=query(first,'interfaces').state,finish=query(last,'interfaces').state,
  startInterfaces=#first.interfaces,endInterfaces=#last.interfaces,bootStable=bootOk==true,
  truncated=first.truncated or last.truncated or false}
 return out
end
return M
