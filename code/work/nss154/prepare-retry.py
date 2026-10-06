from pathlib import Path
import json
r=Path(__file__).resolve().parent
for name in ['epoch-driver','journal','process-identity','pilot-supervisor','restart-harness']:
    source=r/(name+'.mjs');target=r/(name+'-v2.mjs');assert not target.exists()
    text=source.read_text(encoding='utf-8').replace('run1','run2').replace('entry-source-manifest.json','entry-source-manifest-v2.json').replace('frozen-qualified-inputs','frozen-qualified-inputs-v2')
    for dependency in ['session-binding','epoch-driver','journal','process-identity','pilot-supervisor']:
        text=text.replace(dependency+'.mjs',dependency+'-v2.mjs')
    target.write_text(text,encoding='utf-8',newline='')
p=r/'load-v1-reference-private.json';assert not p.exists();p.write_bytes((r/'load-latest-private.json').read_bytes())
with (r/'retry-reason.json').open('x',encoding='utf-8') as f:json.dump({'originalFailurePreserved':True,'failedBeforeCheckpointOrNssStage':True,'supervisorNotKilled':True,'causeObserved':'Lua prerequisite popen read returned nil','readonlyRepeatPassed':True,'rootCauseNotProved':True,'nativeFactoryOrBudgetsChanged':False,'singleRetryOnly':True},f,indent=2);f.write('\n')
print('Original run1 and its actual failure retained; one same-native-factory retry prepared.')
