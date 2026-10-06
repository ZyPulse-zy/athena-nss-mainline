from pathlib import Path
w=Path(__file__).resolve().parents[2];r=w/'work/v21-fiveflow';rates='{tcp:8,tcp2:8,tcp3:8,tcp4:8}'
for n in ['start-dallas.mjs','native-client.mjs','owned-load-policy.mjs']:
 p=r/n;s=p.read_text().replace('{tcp:24,tcp2:8}',rates)
 if n=='native-client.mjs':
  s=s.replace("tcpChildren:[{slot:'tcp',attempt:0,bytes:0,connected:false},{slot:'tcp2',attempt:0,bytes:0,connected:false}]", "tcpChildren:['tcp','tcp2','tcp3','tcp4'].map(slot=>({slot,attempt:0,bytes:0,connected:false}))")
  s=s.replace("['tcp','tcp2'].includes(x.rotateTcp.slot)", "['tcp','tcp2','tcp3','tcp4'].includes(x.rotateTcp.slot)").replace("'CREDIT=32768'","'CREDIT=16384'")
  s=s.replace("await startTcp('tcp',1);await startTcp('tcp2',1);", "for(const slot of ['tcp','tcp2','tcp3','tcp4'])await startTcp(slot,1);")
 if n=='owned-load-policy.mjs':s=s.replace('status.tcpChildren.length===2','status.tcpChildren.length===4')
 p.write_text(s,encoding='utf8')
p=r/'candidate-policy.mjs';s=p.read_text().replace('after.insmodArguments.length<3072','after.insmodArguments.length<2048');p.write_text(s)
p=r/'prepare-runtime.py';s=p.read_text().replace("s=s.replace('after.insmodArguments.length<2048','after.insmodArguments.length<3072')", "# Preserve the existing 2048-character typed module-argument bound.")
p.write_text(s)
p=r/'parse-ecm.mjs';s=p.read_text().replace("selected&&selected.tcp&&selected.udp&&selected.tcp2", "selected&&selected.tcp&&selected.udp&&selected.tcp2&&selected.tcp3&&selected.tcp4").replace('[selected.tcp,selected.udp,selected.tcp2]', '[selected.tcp,selected.udp,selected.tcp2,selected.tcp3,selected.tcp4]').replace('remainingUdpOnly?1:3','remainingUdpOnly?1:5').replace("['tcp2',2399469568]]", "['tcp2',2399469568],['tcp3',2399469568],['tcp4',2399469568]]")
s=s.replace("assert.notEqual(selected.tcp.wan,selected.tcp2.wan,'Two distinct selected WANs required');", "assert.equal(new Set(Object.values(selected).map(f=>f.wan)).size,5,'Five naturally distinct WANs required');")
p.write_text(s)
p=r/'read-controlled.mjs';s=p.read_text().replace('Count -ne 2','Count -ne 4').replace('Two owned SSH children required','Four owned SSH children required').replace('tcpPorts.length<=2','tcpPorts.length<=4')
a=s.index('const pairs=[];');b=s.index('const ownedEstablishedTcpPorts=',a)
s=s[:a]+'''const slots=['tcp','tcp2','tcp3','tcp4'],selected={},pairs=[];
for(const slot of slots){const found=tcp.filter(t=>pc.tcp.some(e=>e.slot===slot&&e.LocalPort===t.identity.original.sport&&e.RemoteAddress===t.identity.original.dst&&e.RemotePort===t.identity.original.dport));assert.ok(found.length<=1);if(found.length)selected[slot]=canonicalSelection(found[0]);}
if(slots.every(slot=>selected[slot]))for(const u of udp){const choice={tcp:selected.tcp,udp:canonicalSelection(u),tcp2:selected.tcp2,tcp3:selected.tcp3,tcp4:selected.tcp4};if(new Set(Object.values(choice).map(f=>f.wan)).size===5&&Object.values(choice).every(f=>!(f.mark&0x2000)))pairs.push(choice);}
''' +s[b:]
p.write_text(s)
p=r/'pilot-supervisor.mjs';s=p.read_text().replace('v20 five-WAN queue map; three exact flows and DOWN18 borrowing','v21 five naturally distinct WANs; four TCP BULK plus UDP RT').replace("selected&&selected.tcp.wan>=1&&selected.tcp.wan<=5&&selected.tcp.wan!==selected.tcp2.wan", "selected&&new Set(Object.values(selected).map(f=>f.wan)).size===5").replace('threeExactFlowMultiWanFunctionalAcceptance:true','fiveExactFlowMultiWanFunctionalAcceptance:true').replace('threeExactFlows:true','fiveExactFlows:true');p.write_text(s)
print('Four 8Mbps owned SSH download children and fixed UDP peer; total32/credit65536 and180s unchanged')
