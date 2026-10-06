"""Distinguish the unchanged native record cap from local pretty-print size."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
source = (root / 'analyze-aba.py').read_text(encoding='utf-8')
old = "assert record_path.stat().st_size <= 1048576\ns = read(record_path)"
assert source.count(old) == 1
source = source.replace(old, "s = read(record_path)\ncompact_record_bytes = len(json.dumps(s,separators=(',',':'),ensure_ascii=False).encode('utf-8'))\nassert compact_record_bytes <= 1048576")
old = "'newCpuComparisonAccepted':None, 'causalCpuReductionPercent':None,"
assert source.count(old) == 1
source = source.replace(old, "'nativeRecordReadLimitBytes':1048576, 'localCompactJsonBytes':compact_record_bytes, 'nativeReadLimitEnforcedByVerifiedStageReader':True,\n          'newCpuComparisonAccepted':None, 'causalCpuReductionPercent':None,")
with (root / 'analyze-aba-v2.py').open('x', encoding='utf-8', newline='') as f:
    f.write(source)
failure = {'passed':False,'source':'work/nss158/analyze-aba.py',
           'error':'AssertionError checking local pretty-printed record size against native wire limit',
           'cause':'Local indentation produced 1381936 bytes, while compact JSON was 693180 bytes; original target read remained capped at 1048576',
           'nativeReadLimitUnchanged':True,'originalSourcePreserved':True,'remoteWrites':False}
with (root / 'analysis-v1-failure.json').open('x',encoding='utf-8') as f:
    json.dump(failure,f,indent=2);f.write('\n')
print('Prepared analysis of native-bounded record; original refusal retained')
