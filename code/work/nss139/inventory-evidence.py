from pathlib import Path
import json
w=Path(__file__).resolve().parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for n in range(129,139):
 r=w/f'work/nss{n}';o={'round':n,'localFiles':sum(p.is_file()for p in r.iterdir()),'qualified':(r/'entry-qualified.json').exists(),'cases':[]}
 for p in sorted(r.glob('controlled-class-*')):
  if not p.is_dir():continue
  c={'case':p.name}
  for f in ['result.json','stage-undo-verified.json','baseline-audit.json','external-recovery-verified.json']:
   if (p/f).exists():
    x=load(p/f);c[f]={'passed':x.get('passed'),'keys':list(x),'errors':x.get('errors')}
  if (p/'last-record-private.json').exists():
   x=load(p/'last-record-private.json');c['record']={k:x.get(k)for k in ['error','classChangeTestCompleted','freshEpochRelearningCompleted','successEarlyCompletion','successRecordGraceSeconds','stageComplete','moduleLoaded','moduleUnloaded','dualPhysicalQueuesRestored','wanRestored','tagsRemoved']}
  o['cases'].append(c)
 if (r/'load-reference-private.json').exists():o['loadDir']=load(r/'load-reference-private.json')['dir']
 print(json.dumps(o))
