import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

export function requireWindowsIdentity(snapshot){
 assert.ok(snapshot.identityReadable===true&&snapshot.processId>0&&snapshot.creationDatePresent===true&&snapshot.executablePathPresent===true&&snapshot.commandLinePresent===true,'Windows process identity unavailable');
 assert.equal(snapshot.networkSocketCommandsPresent,true,'Windows socket inventory unavailable');
 return {passed:true,windowsProcessIdentityReadable:true,networkSocketCommandsPresent:true,trafficGenerated:false,routerWrites:false};
}
export function platformPreflight(){
 const code="$ErrorActionPreference='Stop';$nssSelf=Get-CimInstance Win32_Process -Filter ('ProcessId='+$PID);if(-not $nssSelf){throw 'Current process identity unavailable'};$nssTcp=Get-Command Get-NetTCPConnection -ErrorAction Stop;$nssUdp=Get-Command Get-NetUDPEndpoint -ErrorAction Stop;@{identityReadable=$true;processId=$PID;creationDatePresent=($null -ne $nssSelf.CreationDate);executablePathPresent=([bool]$nssSelf.ExecutablePath);commandLinePresent=([bool]$nssSelf.CommandLine);networkSocketCommandsPresent=([bool]$nssTcp -and [bool]$nssUdp)}|ConvertTo-Json -Compress";
 const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',code],{windowsHide:true,encoding:'utf8',timeout:12000});
 const output='work/v55-resident-trial/platform-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex')+'-private.json';
 fs.writeFileSync(output,JSON.stringify({exitCode:p.status,stdout:p.stdout,stderr:p.stderr,error:p.error?.code??null,trafficGenerated:false,routerWrites:false},null,2)+'\n',{flag:'wx'});
 assert.equal(p.status,0,'Windows identity preflight refused before fixture or router connection; original local output retained');
 return requireWindowsIdentity(JSON.parse(p.stdout.replace(/^\uFEFF/,'')));
}
