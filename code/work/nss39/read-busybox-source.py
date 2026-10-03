"""Fetch the official release for source inspection only; execute nothing from it."""
import urllib.request,tarfile,io,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
url='https://busybox.net/downloads/busybox-1.38.0.tar.bz2'
with urllib.request.urlopen(url,timeout=20) as f: body=f.read(5000001)
assert len(body)<=5000000
with urllib.request.urlopen(url+'.sha256',timeout=20) as f: expected=f.read(512).decode().split()[0]
assert hashlib.sha256(body).hexdigest()==expected
rows=[]
with tarfile.open(fileobj=io.BytesIO(body),mode='r:bz2') as t:
    for name in ['coreutils/timeout.c','libbb/vfork_daemon_rexec.c']:
        b=t.extractfile('busybox-1.38.0/'+name).read();out=root/('busybox-1.38.0-'+Path(name).name);out.write_bytes(b)
        rows.append({'sourcePath':name,'localPath':out.name,'sha256':hashlib.sha256(b).hexdigest()})
result={'url':url,'archiveSha256':expected,'officialChecksumVerified':True,'executed':False,'runningFirmwarePatchesCompared':False,'files':rows}
(root/'busybox-source-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
