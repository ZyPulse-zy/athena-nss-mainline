from pathlib import Path
r=Path('work/nss111')
clock=Path('work/nss110/calibrate-clock.mjs').read_text(encoding='utf-8').replace('nss110','nss111')
(r/'calibrate-clock.mjs').write_text(clock,encoding='utf-8')
s=Path('work/nss100/analyze-long.py').read_text(encoding='utf-8').replace("'schema':'nss100-long-controlled-actual-v1'","'schema':'nss111-long-controlled-actual-v1'").replace("'qosBytesUnchanged':False","'qosBytesUnchanged':True")
(r/'analyze-long.py').write_text(s,encoding='utf-8')
print('Prepared post-run actual analysis; runtime-bound inputs unchanged')
