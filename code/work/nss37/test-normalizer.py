"""Differential normalization and attribute-boundary replay; no router/network IO."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
p=argparse.ArgumentParser();p.add_argument('--wsl-runtime',type=Path);p.add_argument('--capture',type=Path);args=p.parse_args()
old=(here/'original-conntrack-source.lua').read_text();new=(here/'conntrack-source.lua').read_text()
def literal(s):
    assert ']====]' not in s
    return '[====['+s+']====]'
code='local Old=assert(loadstring('+literal(old)+'))();local New=assert(loadstring('+literal(new)+'))()\n'
# Expose only the local pure helper in RAM, without changing candidate bytes.
for name,source in [('OldAttrs',old),('NewAttrs',new)]:
    assert source.count('return M')==1
    code+='local '+name+'=assert(loadstring('+literal(source.replace('return M','return attrs'))+'))()\n'
code+=r'''
local total,attrsChecks,normalChecks,explicitChecks=0,0,0,0
local function same(a,b)if type(a)~=type(b)then return false end;if type(a)~='table'then return a==b end;for k,v in pairs(a)do if not same(v,b[k])then return false end end;for k in pairs(b)do if a[k]==nil then return false end end;return true end
local function assertSame(a,b,label)assert(same(a,b),label);total=total+1 end
local o={version=1,authorizedClient='192.168.237.0/24',conntrackPath='/usr/sbin/conntrack',groupRunnerPath='/root/router-project/classifier/nss23-fixture/group-runner',queryTimeoutSeconds=1,maxQueryAgeSeconds=2,maxSourceBytes=524288,maxSourceRows=2048}
local p={version=1,method='conntrack-cli',exitCode=0,rawStatus=0,boot='fixture',queryFamily='ipv4',queryZone=0,authorizedClient=o.authorizedClient,sequence=1,command=table.concat(Old.argv(o),' '),startedAtUptime=100,finishedAtUptime=100.2}
local row='ipv4 2 udp 17 30 src=192.168.237.207 dst=192.0.2.8 sport=51000 dport=27015 packets=12 bytes=1200 src=192.0.2.8 dst=198.51.100.5 sport=27015 dport=51000 packets=13 bytes=1300 [ASSURED] mark=327680 use=1 id=42'
local function norm(s,err,want,label)
 local a,b,c=pcall(Old.normalize,o,p,s,err or'',p.boot,100.3)
 local x,y,z=pcall(New.normalize,o,p,s,err or'',p.boot,100.3)
 assert(a==x and(not a or(same(b,y)and same(c,z))),label or'normalization difference')
 total=total+1;normalChecks=normalChecks+1
 if want~=nil then assert(a==want,label or'explicit expectation');total=total+1;explicitChecks=explicitChecks+1 end
end
norm(row..'\n','',true,'valid UDP');norm(row:gsub('udp 17 30','tcp 6 30 ESTABLISHED')..'\n','',true,'valid TCP')
norm('','',true,'empty success');norm(row..'\n','conntrack v1.4.7 (conntrack-tools): 1 flow entries have been shown.\n',true,'count receipt')
norm(row..'\n','conntrack v1.4.7 (conntrack-tools): 2 flow entries have been shown.\n',false,'count mismatch')
norm(row..'\n'..row..'\n','',false,'duplicate snapshot id');norm(row,'',false,'truncated')
norm(row..' id=43\n','',false,'duplicate id');norm(row..' zone=1\n','',false,'foreign zone');norm(row..' zone=0 zone=0\n','',false,'duplicate zone')
norm(row:gsub(' id=42','')..'\n','',false,'missing id');norm(row:gsub('mark=327680','mark=4294967296')..'\n','',false,'mark overflow')
norm(row:gsub('id=42','id=042')..'\n','',false,'id leading zero');norm(row:gsub('192.168.237.207','192.168.238.207')..'\n','',false,'foreign LAN')
norm(row..'\r\n','',false,'CR');norm(row..'\0\n','',false,'NUL')
norm('ipv4 2 icmp 1 20 src=192.168.237.207 dst=192.0.2.8 type=8 code=0 id=2 src=192.0.2.8 dst=198.51.100.5 type=0 code=0 id=2 mark=327680 id=42\n','',true,'unsupported ICMP IDs stay ignored')
local whitespace={'',' ','\t','\n','\r','\v','\f','  '}
local prefixes={'','x','not-','x_','id=','mark=','src='}
local values={'','0','00','1','42','4294967295','4294967296','-1','+1','1.5','=','id=8','mark=4','zone=0','a:b','\0'}
for _,k in ipairs({'id','mark','zone'})do for _,w in ipairs(whitespace)do for _,pre in ipairs(prefixes)do for _,v in ipairs(values)do
 local s='head '..pre..w..k..'='..v..w..k..'=17 tail'
 assertSame(OldAttrs(s,k),NewAttrs(s,k),'boundary/value helper difference');attrsChecks=attrsChecks+1
end end end end
local tokens={'id=42','id=0','id=43','xid=42','id=','mark=327680','mark=0','zone=0','zone=1','zone=','src=id=42','x=mark=5','garbage','=','\t','\v','\f'}
for _,a in ipairs(tokens)do for _,b in ipairs(tokens)do for _,space in ipairs({' ','\t','\v','\f'})do
 norm(row..space..a..space..b..'\n','',nil,'suffix mutation')
end end end
for i=1,#row do norm(row:sub(1,i)..'\n','',nil,'all truncation positions')end
local seed=17337
local function rand(n)seed=(seed*48271)%2147483647;return seed%n+1 end
local alphabet=' id=markzone0123456789x_:+-\t\v\f'
for case=1,5000 do
 local s=row
 local at=rand(#s+1);local insert={};for i=1,rand(8)do local k=rand(#alphabet);insert[#insert+1]=alphabet:sub(k,k)end
 s=s:sub(1,at-1)..table.concat(insert)..s:sub(at)
 norm(s..'\n','',nil,'deterministic token fuzz')
end
'''
capture=args.capture
if capture:
    data=json.loads(capture.read_text(encoding='utf-8-sig'))
    code+='norm('+literal(data['stdout'])+','+literal(data['stderr'])+',true,"captured live text normalized equally")\n'
code+="print(string.format('COMPLETE %d attrs=%d normalize=%d explicit=%d',total,attrsChecks,normalChecks,explicitChecks))\n"
file=here/'normalizer-replay-private.lua';file.write_text(code,encoding='utf-8',newline='\n')
def unix(path):
    s=path.resolve().as_posix();return '/mnt/'+s[0].lower()+s[2:]
rt=args.wsl_runtime or root/'work/nss9/lua-runtime/extracted/usr'
r=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/lua5.1'),unix(file)],capture_output=True,text=True,timeout=40)
(here/'normalizer-replay-output.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
m=re.search(r'COMPLETE (\d+) attrs=(\d+) normalize=(\d+) explicit=(\d+)',r.stdout)
out={'passed':r.returncode==0 and m is not None,'checks':int(m[1]) if m else 0,'helperCases':int(m[2]) if m else 0,'normalizationCases':int(m[3]) if m else 0,'explicitExpectations':int(m[4]) if m else 0,'capturedTextReplayed':capture is not None,'sourceSha256':hashlib.sha256(new.encode()).hexdigest(),'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'routerWrites':False,'trafficGenerated':False,'scope':'Pure old/new attributes and normalization under Lua 5.1; deterministic mutations and optional private captured text, no NSS permission or live timestamps.','error':r.stderr}
(here/'normalizer-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out));raise SystemExit(0 if out['passed'] else 1)
