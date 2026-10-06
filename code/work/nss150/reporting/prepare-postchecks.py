from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[3];r=w/'work/nss150'
sources=['calibrate-clock.mjs','verify-all-endpoints.mjs','verify-downloaders.mjs']
for n in sources:
    b=(w/'work/nss147'/n).read_bytes();s=b.replace(b'nss147',b'nss150').replace(b'NSS147',b'NSS150')
    if n=='calibrate-clock.mjs':s=s.replace(b'controlled-matched-aba-',b'automatic-epoch-')
    if n=='verify-all-endpoints.mjs':
        a=b'rounds=[129,131,132,133,135,136,138,144,145,146,147]'
        assert s.count(a)==1;s=s.replace(a,b'rounds=[129,131,132,133,135,136,138,144,145,146,147,149,150]')
    if n=='verify-downloaders.mjs':
        # Identical download-server source in 147, 149 and 150; only Windows
        # application paths differ. Assert this before relying on exact argv.
        assert (w/'work/nss147/download-server.py').read_bytes()==(w/'work/nss149/download-server.py').read_bytes()==(w/'work/nss150/download-server.py').read_bytes()
    with (r/n).open('xb') as f:f.write(s)
print(json.dumps({'prepared':True,'readonlyPostchecksOnly':True,'existingEndpointLoads':13,'downloadSourceIdentical':True,'routerWrites':False}))
