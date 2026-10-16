local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local base=assert(arg[1]);local hash=assert(arg[2]);local reason=assert(arg[3]);assert(base:match('^/root/router%-project/classifier/[%w%-]+$'))
assert(#hash==64 and hash:match('^[0-9a-f]+$'));assert(reason=='service-stop'or reason=='unhealthy-terminal'or reason=='rollback')
local ram='/tmp/router-project-game-classifier';local function read(p,cap)local f=io.open(p);if not f then return nil end;local s=f:read(cap+1)or'';f:close();assert(#s<=cap);return s end
local boot=assert(read('/proc/sys/kernel/random/boot_id',128)):gsub('%s+$','')
local info=assert(read('/proc/'..n.getpid()..'/fdinfo/8',8192));assert(info:match('FLOCK%s+ADVISORY%s+WRITE'));assert(fs.readlink('/proc/'..n.getpid()..'/fd/8')=='/tmp/router-project-transaction.lock')
local d,a,b=fs.lstat(ram);if not d then assert(a==2 or b==2);print('{"noWorker":true}');os.exit(0)end
assert(d.type=='dir'and d.uid==0 and d.gid==0 and d.modedec==700)
local generation=base:match('/([^/]+)$');assert(read(ram..'/owner',256)==generation..' '..boot..'\n')
local marker=ram..'/stopped';local st,a,b=fs.lstat(marker);if st then assert(st.type=='reg'and st.nlink==1 and st.uid==0 and st.gid==0)else assert(a==2 or b==2)end
local previous=read(marker,256);if previous~='unhealthy-terminal\n'or reason=='rollback'then local f=assert(io.open(marker,'w'));assert(f:write(reason..'\n'));assert(f:close());assert(fs.chmod(marker,600))end
local expected=table.concat({'/usr/bin/lua',base..'/worker.lua','watch',base,hash},'\0')..'\0';local selected={}
for name in fs.dir('/proc')do if name:match('^%d+$')then
 local pid=tonumber(name);local cmd=read('/proc/'..name..'/cmdline',8192)
 if cmd==expected then local text=read('/proc/'..name..'/stat',8192);if text then local a={};for v in assert(text:match('^%d+ %b() (.*)$')):gmatch('%S+')do a[#a+1]=v end;selected[#selected+1]={pid=pid,start=a[20]}end end
end end
assert(#selected<=1,'Classifier singleton violated')
for _,p in ipairs(selected)do
 local cmd=base..'/process-stop '..p.pid..' '..p.start..' '..boot..' /usr/bin/lua '..base..'/worker.lua watch '..base..' '..hash
 local f=assert(io.popen(cmd..'; r=$?; printf "\n__NSS23_STOP_RC__%s\n" "$r"'));local raw=f:read(4096);f:close();local body,rc=raw:match('^(.*)\n__NSS23_STOP_RC__(%d+)\n$');assert(body and rc=='0');local result=assert(j.parse(body));assert(result.ok)
end
print(j.stringify({stopMarkerWritten=true,exactWorkersStopped=#selected,pidfdUsed=true}))
