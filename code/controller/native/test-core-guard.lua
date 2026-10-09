-- Pure tests: no router, process, queue, firmware or filesystem mutations.
local root=assert(arg[0]:match('^(.*)/[^/]+$'));local m=dofile(root..'/core_guard_permission.lua')
local r={phase='native-running',running=true,nativeRun=true,hardwareAdmissionEnabled=true,flowState={sourceFresh=true},supervisedOwnerPid=1,supervisedOwnerStart='10',guardianPid=2,guardianStart='20'}
local d={summary={sourceFresh=true,atUptime=100}}
local gate='abi=2 capacity=32 stopping=0 firmware_receipts=1\nslot=0 state=1 generation=1 '
local function process(pid,start,mode)return pid==1 and start=='10' and mode=='foreground' or pid==2 and start=='20' and mode=='guard' end
local count=0;local function check(expected,h,g,at,p)count=count+1;assert(m.allowed(r,d,h or 100,g or gate,at or 101,p or process)==expected,'Permission case '..count)end
check(true)
check(false,90);check(false,110);check(false,100,gate:gsub('abi=2','abi=1'));check(false,100,gate:gsub('stopping=0','stopping=1'))
check(false,100,gate:gsub('state=1','state=5'));check(false,100,gate,101,function()return false end)
r.phase='rolling-back';check(false);r.phase='native-running'
r.running=false;check(false);r.running=true
r.nativeRun=false;check(false);r.nativeRun=true
r.hardwareAdmissionEnabled=false;check(false);r.hardwareAdmissionEnabled=true
r.flowState.sourceFresh=false;check(false);r.flowState.sourceFresh=true
d.summary.sourceFresh=false;check(false);d.summary.sourceFresh=true
d.summary.atUptime=90;check(false);d.summary.atUptime=110;check(false);d.summary.atUptime=100
r.guardianStart='21';check(false);r.guardianStart='20';check(true)
print('core-guard-permission-models-passed '..count)
