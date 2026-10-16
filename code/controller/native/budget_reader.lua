-- Child of the native guardian, reaped by its independent rollback.
local root=assert(arg[0]:match('^(.*)/[^/]+$'))
local j=require('luci.jsonc');local n=require('nixio');local fs=require('nixio.fs')
local collector=dofile(root..'/collector.lua')
local sampler=dofile(root..'/budget_sampler.lua')
local profile=dofile(root..'/wan_contract.lua').load(root)
local f=assert(io.open('/proc/sys/kernel/random/boot_id'));local boot=f:read(128):match('%S+');f:close()
local function publish(name,value)
 local p=root..'/'..name;local f=assert(io.open(p..'.new','w'))
 assert(f:write(type(value)=='table' and j.stringify(value) or tostring(value)))
 assert(f:close());assert(fs.rename(p..'.new',p))
end
sampler.run({now=collector.now,collect=collector.software_budgets,publish=publish,
 stopped=function()return fs.stat(root..'/stop')~=nil end,
 sleep=function(seconds)n.nanosleep(math.floor(seconds),math.floor((seconds%1)*1000000000))end},profile.wanCount,boot)
