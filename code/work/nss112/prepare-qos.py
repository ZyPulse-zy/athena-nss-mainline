from pathlib import Path
import json,hashlib
r=Path('work/nss112');s=Path('work/nss105/qos-physical.lua').read_text(encoding='utf-8')
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
replace('function M.validateNative(qraw,craw,complete)','function M.validateNative(qraw,craw,complete,up)\n if up then assert(not qraw:find(" 8f%x*:")and not craw:find(" 8f%x*:"),"Downstream tag on uplink");qraw=qraw:gsub("8e","8f");craw=craw:gsub("8e","8f")end')
replace('function M.new(P,fs,j,command,now,stopped,record)','function M.new(P,fs,j,command,now,stopped,record,up)')
replace("local d=assert(P.qosDevice);assert(d=='lan1'or d=='lan4');", "local d=assert(up and P.uplinkDevice or P.qosDevice);assert(up and d=='wan'or not up and(d=='lan1'or d=='lan4'));")
replace('shape(P.qosBaseline)','shape(up and P.uplinkBaseline or P.qosBaseline)')
replace('validation=M.validateNative(q,c,complete)', 'validation=M.validateNative(q,c,complete,up),device=d')
replace("assert(not fs.lstat('/sys/module/qca_nss_qdisc'));assert(base(),'Physical default queues drifted');", "if up then assert(record.sharedModuleOwnedByDown==true and fs.lstat('/sys/module/qca_nss_qdisc'));assert(P.uplinkIfindex==6 and tonumber(command('/bin/cat /sys/class/net/wan/ifindex'))==6)else assert(not fs.lstat('/sys/module/qca_nss_qdisc'))end;assert(base(),'Physical default queues drifted');")
replace("ownedModule=true;command('/sbin/insmod '..mod);assert(fs.lstat('/sys/module/qca_nss_qdisc'));record.qosModuleLoaded=true", "ownedModule=true;if not up then command('/sbin/insmod '..mod)end;assert(fs.lstat('/sys/module/qca_nss_qdisc'));record.qosModuleLoaded=not up")
replace("stopped();command(tc..' '..c);record.qosCommandsCompleted", "stopped();if up then c=c:gsub('8f','8e')end;command(tc..' '..c);record.qosCommandsCompleted")
replace("raw:find('qdisc nsshtb 8f00:',1,true)", "raw:find('qdisc nsshtb '..(up and'8e00:'or'8f00:'),1,true)")
replace('M.validateNative(raw,c,false)', 'M.validateNative(raw,c,false,up)')
replace("assert(trim(command('/bin/ls -A /sys/module/qca_nss_qdisc/holders'))=='','Foreign NSS qdisc holder');", "if up then assert(base());ownedModule=false;record.qosRestored=true;record.sharedModuleReferenceReleased=true;record.qosAfterUndo=assert(j.parse(command('/sbin/tc -j -s -d qdisc show dev '..d)));return end;assert(trim(command('/bin/ls -A /sys/module/qca_nss_qdisc/holders'))=='','Foreign NSS qdisc holder');")
replace('return M\n', '''local C={validateNative=M.validateNative}
function C.new(P,fs,j,command,now,stopped,record)
 assert(P.uplinkDevice=='wan'and P.uplinkIfindex==6 and P.uplinkPhysicalAeId==5)
 local down=M.new(P,fs,j,command,now,stopped,record,false)
 record.uplinkQos={};local up=M.new(P,fs,j,command,now,stopped,record.uplinkQos,true);local out={}
 function out.setup(deadline)
  local d=down.setup(deadline);record.uplinkQos.sharedModuleOwnedByDown=record.qosModuleLoaded==true
  d.uplink=assert(j.parse(j.stringify(up.setup(deadline))));record.dualPhysicalQueuesReady=true;return d
 end
 function out.snapshot()local d=down.snapshot();d.uplink=up.snapshot();return d end
 function out.cleanup()
  local a,x=pcall(up.cleanup);local b,y=pcall(down.cleanup)
  assert(a,x);assert(b,y);record.dualPhysicalQueuesRestored=record.qosRestored==true and record.uplinkQos.qosRestored==true
 end
 return out
end
return C
''')
(r/'qos-physical.lua').write_text(s,encoding='utf-8')
(r/'qos-change.json').write_text(json.dumps({'changedVariable':'add physical wan uplink shaper and corresponding leaf tags','downstreamQosRatesUnchanged':True,'uplinkRoot':'8e00:','uplinkBulkLeaf':'8e05:','uplinkRtLeaf':'8e06:','oneSharedOwnedQdiscModule':True,'cleanupOrder':['uplink root','downlink root','owned module'],'independentOwnerSeconds':100,'sourceSha256':hashlib.sha256(s.encode()).hexdigest(),'hardwareExecution':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'qosBytes':len(s.encode()),'hardwareExecution':False}))
