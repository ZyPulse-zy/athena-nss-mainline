"""Change only the owned four-TCP fixture transport; keep the five-slot data plane."""
from pathlib import Path
import shutil

w=Path(__file__).resolve().parents[1]
old=w/'work/v24-fiveflow'; r=w/'work/v27-raw'; r.mkdir()
for p in old.iterdir():
    if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1'] or any(s in p.name for s in ['qualify','failed','inspect-ssh','model-serial']):continue
    b=p.read_bytes().replace(b'work/v24-fiveflow',b'work/v27-raw').replace(rb'work\/v24-fiveflow\/',rb'work\/v27-raw\/').replace(b'v24-fiveflow-',b'v27-raw-')
    if p.name=='session-binding.mjs':b=b.replace(b'../v23-fiveflow/session-binding.mjs',b'../v24-fiveflow/session-binding.mjs')
    if p.name=='pilot-supervisor.mjs':b=b.replace(b'v24 five',b'v27 raw five').replace(b'wait-four-ssh.mjs',b'wait-four-raw.mjs')
    (r/p.name).write_bytes(b)
for n in ['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json']:shutil.copy2(old/n,r/n)
print('v27 cloned; five-slot native and all data-plane Lua unchanged')
