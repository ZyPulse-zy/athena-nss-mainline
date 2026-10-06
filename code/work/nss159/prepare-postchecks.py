from pathlib import Path
r=Path('work/nss159');evening=Path('work/nss158')
def write(p,s):
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
s=(evening/'calibrate-clock.mjs').read_text(encoding='utf-8').replace('nss158\\/','nss159\\/')
write(r/'calibrate-clock.mjs',s)
s=(evening/'analyze-aba-v2.py').read_text(encoding='utf-8')
s=s.replace('work/nss158/automatic-epoch-','work/nss159/automatic-epoch-').replace('nss158-controlled-upload-aba-v1','nss159-controlled-download-aba-v1')
s=s.replace("'direction':'upload'", "'direction':'download'").replace("'tcpMetric':'server-confirmed received bytes'", "'tcpMetric':'application received payload bytes'").replace("'downlinkMainlyAckAndSmallUdp':True", "'downlinkMainlyAckAndSmallUdp':False")
s=s.replace("'uploadMbps':p['whole']['clientTcpMbps']", "'downloadMbps':p['whole']['clientTcpMbps']")
write(r/'analyze-download.py',s)
s=(evening/'compare-load.py').read_text(encoding='utf-8')
s=s.replace("['wan']['txMbps']", "['wan']['rxMbps']").replace('server_received_throughput_spread_le_10percent','client_received_throughput_spread_le_10percent').replace('physical_wan_transmit_spread_le_10percent','physical_wan_receive_spread_le_10percent')
s=s.replace('serverConfirmedMbps','clientReceivedMbps').replace('physicalWanTransmitMbps','physicalWanReceiveMbps').replace('TCP upload about 30 Mbps','TCP download offered 32 Mbps, with NSS DOWN30 budget')
write(r/'compare-download.py',s)
s=(evening/'evening-verify-all-endpoints.mjs').read_text(encoding='utf-8')
needle="const hashes=loads.map"
assert needle in s
insert="""const downloadRoot='work/nss159';
const downloadDirs=fs.readdirSync(downloadRoot,{withFileTypes:true}).filter(d=>d.isDirectory()&&/^load-\\d{14}-[a-f0-9]{16}$/.test(d.name)).map(d=>downloadRoot+'/'+d.name).sort();
for(const dir of downloadDirs){const s=JSON.parse(fs.readFileSync(dir+'/server-deadline-private.json'));assert.match(s.unit,/^nss159-[a-f0-9]{16}$/);assert.equal(s.verifiedBeforeClientTraffic,true);assert.equal(s.independentOsDeadlineSeconds,250);assert.ok(!loads.some(x=>x.unit===s.unit));loads.push({dir,unit:s.unit});}
"""
s=s.replace(needle,insert+needle)
write(evening/'evening-verify-all-endpoints-v2.mjs',s)
s=(evening/'evening-verify-downloaders.mjs').read_text(encoding='utf-8')
s=s.replace("const body=fs.readFileSync('work/nss150/download-server.py','utf8');", "const bodies=['work/nss150/download-server.py','work/nss159/download-server.py'].map(f=>fs.readFileSync(f,'utf8'));")
s=s.replace('body=${JSON.stringify(body)}','bodies=${JSON.stringify(bodies)}').replace('body in argv','any(body in argv for body in bodies)')
write(evening/'evening-verify-downloaders-v2.mjs',s)
print('Prepared download analysis and evening closure for every exact NSS159 owned load')
