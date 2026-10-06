"""Retain the second copy error; restore the new v22 qualifier, not v21's model entry."""
from pathlib import Path
import json
import shutil

r = Path(__file__).resolve().parent
shutil.copy2(r / 'qualify-entry.mjs', r / 'failed-qualification-copy-scope-v2.mjs')
with (r / 'failed-qualification-copy-scope-v2.json').open('x', encoding='utf-8') as f:
    json.dump({'passed': False, 'error': 'Byte repair copied the old qualifier into the new qualifier path',
               'missingModelInputRejectedBeforeHardware': True, 'productionWrites': False,
               'originalFailedQualifierRetained': True}, f, indent=2)
    f.write('\n')
shutil.copy2(r / 'failed-qualification-newlines-v1.mjs', r / 'qualify-entry.mjs')
print('New v22 inventory qualifier restored; both copy failures retained')
