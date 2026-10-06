"""Repair copy newline changes; preserve v21 and the one v22 inventory change."""
from pathlib import Path
import json
import shutil

w = Path(__file__).resolve().parents[2]
old = w / 'work/v21-fiveflow'
new = w / 'work/v22-fiveflow'
shutil.copy2(new / 'qualify-entry.mjs', new / 'failed-qualification-newlines-v1.mjs')
with (new / 'failed-qualification-newlines-v1.json').open('x', encoding='utf-8') as f:
    json.dump({'passed': False, 'error': 'pack-json.mjs changed outside inventory scope: CRLF versus LF from text copy',
               'qualifierRejectedBeforePcSyntaxAndManifest': True, 'hardwareExecuted': False,
               'productionWrites': False, 'priorSourceUnmodified': True}, f, indent=2)
    f.write('\n')
for p in old.iterdir():
    if not p.is_file() or not (new / p.name).is_file() or p.suffix not in ['.mjs', '.lua', '.py', '.ps1']:
        continue
    if p.name == 'read-controlled.mjs':
        continue
    data = p.read_bytes().replace(b'work/v21-fiveflow', b'work/v22-fiveflow')
    if p.name == 'session-binding.mjs':
        data = data.replace(b'../v20-five/session-binding.mjs', b'../v21-fiveflow/session-binding.mjs')
    if p.name == 'module-stage.mjs':
        for name in [b'endpoint-gate', b'runtime-elf-comparison.json', b'native-source-qualified.json']:
            data = data.replace(b'work/v22-fiveflow/' + name, b'work/v21-fiveflow/' + name)
    (new / p.name).write_bytes(data)
print('Unchanged copied sources restored to exact original bytes, with declared root-path replacements only')
