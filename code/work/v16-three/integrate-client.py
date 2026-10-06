"""Bind both native SSH children to Windows sockets before observing CTs."""
from pathlib import Path
r=Path(__file__).resolve().parent
p=r/'read-controlled.mjs';s=p.read_text();a=s.index("if(-not $s.tcpOwnerPid)");b=s.index('const pcRaw=',a)
replacement="""if(@($s.tcpChildren).Count -ne 2){throw 'Two owned SSH children required'};$rows=@();foreach($v in $s.tcpChildren){$k=Get-CimInstance Win32_Process -Filter ('ProcessId='+$v.ownerPid);if($k.ParentProcessId -ne $p.Id -or $k.ExecutablePath -ne $v.executable -or -not $k.CommandLine.Contains('sub2api-dallas') -or -not $k.CommandLine.Contains('python3 -u -c') -or [math]::Abs(([datetime]$k.CreationDate).ToUniversalTime().Subtract([datetime]::Parse($v.spawnedAt).ToUniversalTime()).TotalSeconds) -gt 3){throw 'Owned SSH child identity changed'};foreach($e in @(Get-NetTCPConnection -OwningProcess $v.ownerPid -State Established -ErrorAction SilentlyContinue)){$rows+=@{LocalAddress=$e.LocalAddress;LocalPort=$e.LocalPort;RemoteAddress=$e.RemoteAddress;RemotePort=$e.RemotePort;slot=$v.slot}}};@{pid=$p.Id;tcp=@($rows);udp=@(Get-NetUDPEndpoint -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort)}|ConvertTo-Json -Depth 5 -Compress`;
"""
s=s[:a]+replacement+s[b:]
s=s.replace('tcpPorts.length<=1','tcpPorts.length<=2')
a=s.index('const pairs=[];');b=s.index('const ownedEstablishedTcpPorts=',a)
s=s[:a]+"""const pairs=[];for(const t of tcp)for(const t2 of tcp)for(const u of udp){
 const a=pc.tcp.find(e=>e.LocalPort===t.identity.original.sport),b=pc.tcp.find(e=>e.LocalPort===t2.identity.original.sport);
 if(a?.slot==='tcp'&&b?.slot==='tcp2'&&t.identity.wan!==t2.identity.wan&&!(t.identity.mark&0x2000)&&!(t2.identity.mark&0x2000))pairs.push({tcp:canonicalSelection(t),udp:canonicalSelection(u),tcp2:canonicalSelection(t2)});
}
"""+s[b:];p.write_text(s)
p=r/'match-controlled.mjs';s=p.read_text().replace('frame.ownedEstablishedTcpPorts.length===1','frame.ownedEstablishedTcpPorts.length===2').replace('onlyOneOwnedTcpRemaining:true','twoOwnedTcpChildrenAndOneUdp:true')
s=s.replace('if(frame.tcp.length===1&&frame.udp.length===1&&status.tcpConnected){','if(frame.tcp.length===2&&frame.udp.length===1&&status.tcpConnected){')
a=s.index('  assert.ok(status.tcpAttempt<8');b=s.index('\n }',a)
s=s[:a]+"""  const slot=status.tcpChildren.find(x=>x.slot==='tcp2');assert.ok(slot.attempt<8,'Eight fixed-UDP second TCP candidates exhausted');
  fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:config.session,rotateTcp:{slot:'tcp2',attempt:slot.attempt+1}}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');"""+s[b:]
s=s.replace('twoWans:[frame.pairs[0].tcp.wan,frame.pairs[0].udp.wan]','naturalWanSet:[...new Set(Object.values(frame.pairs[0]).map(x=>x.wan))]')
p.write_text(s)
print('Three exact application sockets integrated, no client started')
