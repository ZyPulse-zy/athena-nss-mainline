-- Capture current config hashes in this candidate's private RAM directory.
-- No service, queue, network, firmware or module changes.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
assert(root=='/tmp/athena-dorm-native')
local fs=require('nixio.fs');local j=require('luci.jsonc')
assert(not fs.stat(root..'/lock') and not fs.stat('/sys/module/athena_ecm_gate'))
local function run(c)
 local f=assert(io.popen(c..' 2>&1; printf "\\nATHENA_EXIT_%s\\n" "$?"'))
 local s=f:read('*a');f:close();local body,code=s:match('^(.*)\nATHENA_EXIT_(%d+)\n$')
 assert(body and code=='0',s);return body
end
local function sha(p)return assert(run('/usr/bin/sha256sum '..p):match('^(%x+) '))end
local f=assert(io.open(root..'/build-result.json'));local pins=assert(j.parse(f:read('*a')));f:close()
assert(pins.passed and run('/bin/uname -r'):match('^6%.18%.44%s*$'))
assert(sha('/lib/modules/6.18.44/ecm.ko')==pins.ecmOriginalSha256)
assert(sha('/lib/modules/6.18.44/qca-nss-drv.ko')==pins.driverSha256)
assert(sha('/lib/modules/6.18.44/act_nssmirred.ko')==pins.ingressOriginalSha256)
for _,name in ipairs({'athena_ecm_gate.ko','athena_nss_receipts.ko'})do assert(sha(root..'/'..name)==pins[name].sha256)end
assert(sha(root..'/ecm-receipts.ko')==pins.ecmReceiptCopySha256)
assert(sha(root..'/act_nssmirred-receipts.ko')==pins.ingressReceiptCopySha256)
pins.protected={}
for _,p in ipairs({'/etc/config/network','/etc/config/firewall','/etc/config/wireless',
 '/root/router-project/classifier/nss23-20261002122153-58e283ed/config.json'})do pins.protected[p]=sha(p)end
assert(fs.chmod(root,'700'));f=assert(io.open(root..'/pins.json.new','w'))
assert(f:write(j.stringify(pins)));assert(f:close());assert(fs.chmod(root..'/pins.json.new','600'))
assert(fs.rename(root..'/pins.json.new',root..'/pins.json'))
print(j.stringify({prepared=true,dataPlaneWrites=false,privateBaseline=true,kernel='6.18.44'}))
