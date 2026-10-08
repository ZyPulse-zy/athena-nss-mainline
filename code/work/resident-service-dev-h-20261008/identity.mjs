import {spawnSync} from 'node:child_process';import assert from 'node:assert/strict';import path from 'node:path';
import {serviceRoot,resolveLocal} from './storage.mjs';
export function processIdentity(pid){
 assert.ok(Number.isInteger(pid)&&pid>0);
 const target=resolveLocal(serviceRoot+'/daemon.mjs').replaceAll("'","''");
 const code="$ErrorActionPreference='Stop';$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+pid+"';if(-not $p){@{found=$false}|ConvertTo-Json -Compress;exit 0};@{found=$true;pid=[int]$p.ProcessId;birth=$p.CreationDate.ToUniversalTime().ToString('o');executable=[string]$p.ExecutablePath;expectedCommand=([bool]$p.CommandLine -and $p.CommandLine.Contains('"+target+"') -and $p.CommandLine -match '\\brun(?:\\s|$)')}|ConvertTo-Json -Compress";
 const p=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',code],{encoding:'utf8',windowsHide:true,timeout:12000,maxBuffer:65536});assert.equal(p.status,0,'Resident process identity unavailable');return JSON.parse(p.stdout.replace(/^\uFEFF/,''));
}
export function sameProcess(actual,expected){return actual.found===true&&actual.pid===expected.pid&&actual.birth===expected.birth&&actual.executable.toLowerCase()===expected.executable.toLowerCase()&&actual.expectedCommand===true;}
