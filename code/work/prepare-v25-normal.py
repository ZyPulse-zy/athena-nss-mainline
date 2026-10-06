"""Bridge normal application-owned flows to the proven three-slot multi-WAN data plane."""
from pathlib import Path
import shutil

w = Path(__file__).resolve().parents[1]; old = w / 'work/v20-five'; r = w / 'work/v25-normal'; r.mkdir()
names = ['class-leaf-map.mjs','classified-tags.lua','classifier.lua','fast-path.lua','wan-scope.lua',
         'qos-physical.lua','tag-normalizer.lua','module-stage-guardian.lua','module-stage.mjs','payload.mjs',
         'parse-ecm.mjs','wan-tag-plan.mjs','current-audit-diagnostic.mjs']
for name in names:
    data = (old / name).read_bytes().replace(b'work/v20-five', b'work/v25-normal').replace(rb'work\/v20-five\/', rb'work\/v25-normal\/')
    (r / name).write_bytes(data)
for name in ['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json']:
    shutil.copy2(old / name, r / name)
data = (w / 'work/v11/read-real-candidates.mjs').read_bytes().replace(b'work/v11', b'work/v25-normal')
(r / 'read-real-candidates.mjs').write_bytes(data)
data = (old / 'epoch-driver.mjs').read_bytes().replace(b'work/v20-five', b'work/v25-normal').replace(rb'work\/v20-five\/', rb'work\/v25-normal\/')
data = data.replace(b'export async function runEpoch(continuityPath,onDetached,expectedExit=false){', b'export async function runEpoch(continuityPath,onDetached,expectedExit=false){')
start = data.index(b" const load=JSON.parse(fs.readFileSync(observationRoot+'/load-latest-private.json'));")
end = data.index(b" const preauditQualification=", start)
data = data[:start] + b" save('normal-application-preaudit-private',{candidates,pc:JSON.parse(fs.readFileSync(observationRoot+'/pc-app-endpoints-private.json'))});\r\n" + data[end:]
data = data.replace(b'trafficGenerated:true', b'trafficGenerated:false').replace(b'realCs2SteamPair:false,controlledRealWanPair:true', b'realCs2SteamPair:true,controlledRealWanPair:false')
data = data.replace(b'controlledOwnerRequired:true', b'realApplicationOwnershipRequired:true')
data = data.replace(b'TWO_WAN_CONTROLLED_PAIR_VISIBLE_NOT_STARTED', b'MULTI_WAN_NORMAL_APPLICATION_TRIPLE_VISIBLE_NOT_STARTED').replace(b'WAITING_FOR_CONTROLLED_OWNED_PAIR', b'WAITING_FOR_CS2_AND_TWO_STEAM_BULK_FLOWS')
(r / 'epoch-driver.mjs').write_bytes(data)
print('v25 normal applications adapter; proven v20 native/Lua/QoS bytes retained, no fixture generator')
