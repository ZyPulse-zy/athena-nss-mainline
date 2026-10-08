from pathlib import Path
import subprocess, json
w=Path(__file__).resolve().parents[2]
old=w/'work/resident-task-dev-i-20261008/upgrade.ps1'
out=w/'work/resident-task-continuous-20261008'
out.mkdir(exist_ok=False)
text=old.read_text(encoding='utf-8')
text=text.replace("'work/resident-service-dev-h-20261008/service-launch.ps1'","'work/resident-service-dev-i-20261008/service-launch.ps1'")
text=text.replace("$nssNewLauncher=Join-Path $nssWorkspace 'work/resident-service-dev-i-20261008/service-launch.ps1'","$nssNewLauncher=Join-Path $nssWorkspace 'work/resident-continuous-dev-20261008/service-launch.ps1'")
text=text.replace("'work/resident-service-dev-i-20261008/daemon.mjs'","'work/resident-continuous-dev-20261008/daemon.mjs'")
text=text.replace('dev-i-scheduled-task','continuous-scheduled-task').replace('dev-i-task-upgrade','continuous-task-upgrade')
text=text.replace("candidate='dev-i'","candidate='continuous'")
assert "'work/resident-service-dev-i-20261008/service-launch.ps1'" in text
assert "'work/resident-continuous-dev-20261008/service-launch.ps1'" in text
with (out/'upgrade.ps1').open('x',encoding='utf-8',newline='') as f:f.write(text)
p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"$t=$null;$e=$null;[void][Management.Automation.Language.Parser]::ParseFile('"+str(out/'upgrade.ps1').replace("'","''")+"',[ref]$t,[ref]$e);if($e.Count){throw ($e|Out-String)}"],capture_output=True,text=True,encoding='utf-8')
with (out/'syntax-private.json').open('x',encoding='utf-8') as f:json.dump({'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},f)
assert p.returncode==0,p.stderr
print(json.dumps({'passed':True,'preparedOnly':True,'onlyOwnedActionUpgrade':True,'otherTaskSettingsPreserved':True,'output':'work/resident-task-continuous-20261008/upgrade.ps1'}))
