import tempfile,subprocess,json,os,shutil
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'code/controller/native';tests=[]
for fail in [None,'verify-checkpoint','verify-restoration','unload','load-candidate','verify-recovery','persist-candidate']:
 with tempfile.TemporaryDirectory()as folder:
  root=Path(folder)
  for private, public in [('driver-runtime.sh','wifi-driver-runtime.sh'),('driver-guardian.sh','wifi-driver-guardian.sh')]:shutil.copyfile(base/public,root/private)
  (root/'model-action').write_text('#!/bin/sh\nset -eu\nprintf "%s\\n" "$1" >> "'+str(root/'actions')+'"\nif test "$1" = "'+str(fail)+'" && test ! -f "'+str(root/'fail-used')+'"; then touch "'+str(root/'fail-used')+'"; exit 1; fi\n');(root/'model-action').chmod(0o700)
  env=os.environ|{'ATHENA_DRIVER_MODEL':'1'}
  run=subprocess.run(['sh',str(root/'driver-runtime.sh'),str(root),'run'],env=env)
  if fail in [None,'persist-candidate']:
   assert run.returncode==0
   persist=subprocess.run(['sh',str(root/'driver-runtime.sh'),str(root),'persist'],env=env)
   assert (persist.returncode==0)==(fail is None)
  else:assert run.returncode!=0
  guard=subprocess.run(['sh',str(root/'driver-guardian.sh'),str(root),'0'],env=env,timeout=5);assert guard.returncode==0
  actions=(root/'actions').read_text().splitlines()
  if fail is None:assert (root/'committed').exists()and'load-original'not in actions
  elif fail in ['verify-checkpoint','verify-restoration']:assert 'unload'not in actions
  else:assert 'load-original'in actions and(root/'outcome').read_text().strip()=='restored'
  tests.append({'failureOnce':fail,'passed':True,'mockedAllRouterActions':True})
print(json.dumps({'passed':True,'tests':tests,'routerModified':False,'kernelFirmwareIOMocked':True}))
print('Seven runtime/guardian/persistence models passed')
