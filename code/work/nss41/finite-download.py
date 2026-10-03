"""Bounded TCP download only; each curl has its own transfer deadline."""
import json,subprocess,sys,time
from pathlib import Path
root=Path(sys.argv[1]);assert root.is_dir()
size=64*1024*1024;count=8
url=f'https://speed.cloudflare.com/__down?bytes={size}'
cmd=['curl.exe','--ipv4','--http1.1','--fail','--max-time','25','--connect-timeout','5','--max-filesize',str(size),'--output','NUL','--write-out','%{json}',url]
began=time.perf_counter();children=[];rows=[]
try:
    for i in range(count):
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        children.append((i,p));time.sleep(.05)
    for i,p in children:
        out,err=p.communicate(timeout=max(.1,29-(time.perf_counter()-began)))
        try:metrics=json.loads(out)
        except json.JSONDecodeError:metrics={}
        assert metrics.get('size_download',0)<=size
        rows.append({'slot':i,'exitCode':p.returncode,'metrics':metrics,'stderr':err[-2000:]})
finally:
    for i,p in children:
        if p.poll() is None:p.terminate()
    for i,p in children:
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
    result={'scope':'Finite ordinary TCP download; not Steam or CS2','seconds':time.perf_counter()-began,'connections':count,'bytesPerRequestCeiling':size,'aggregateByteCeiling':size*count,'eachCurlHardDeadlineSeconds':25,'allChildrenExited':all(p.poll() is not None for _,p in children),'routerConfigurationWrites':False,'rows':rows}
    (root/'download-result-private.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'connections':count,'downloadedBytes':sum(r['metrics'].get('size_download',0) for r in rows),'seconds':result['seconds'],'allChildrenExited':result['allChildrenExited'],'successfulRequests':sum(r['exitCode']==0 for r in rows)}))
