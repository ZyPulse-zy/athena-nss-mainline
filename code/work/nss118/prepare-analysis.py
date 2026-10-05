from pathlib import Path
r=Path('work/nss118')
for name in ['health.mjs','read-final-physical.mjs','prove-upstream.py','analyze-long.py','calibrate-clock.mjs','analyze-uplink-transient.py']:
 s=(Path('work/nss117')/name).read_text(encoding='utf-8').replace('nss117','nss118').replace('NSS117','NSS118')
 if name=='calibrate-clock.mjs':s=s.replace('work\\/nss116\\/','work\\/nss118\\/')
 if name=='analyze-long.py':s=s.replace("'offeredTcpMbps':48","'offeredTcpMbps':32")
 if name=='analyze-uplink-transient.py':s=s.replace('Reduce only offered upload from 48 to 32 Mbps; keep queues and all gate deadlines exact.','Inspect actual transfer and RT results before another single-variable change.')
 (r/name).write_text(s,encoding='utf-8')
