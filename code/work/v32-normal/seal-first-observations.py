"""Preserve the observed first client window without asserting NSS acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

w=Path(__file__).resolve().parents[2]
r=w/'work/v32-normal'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
q=read(r/'entry-qualified.json')
closure=Path(read(r/'first-window-closure-pointer.json')['directory'])
assert q['passed'] and not q['hardwareExecuted']
for name,digest in q['sourceManifest'].items():
    data=(w/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest,name
    target=closure/'frozen-sources'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
private_names=['client-before-observed.json','controlled-candidates-private.json',
 'controlled-pc-raw-private.json','normal-reader-process-private.json',
 'pc-app-endpoints-private.json','real-candidates-private.json',
 'real-candidates-raw-private.json','real-reader-qualified.json',
 'steam-start-events-private.json','entry-qualified.json','prepare-receipt.json']
saved={}
for name in private_names:
    data=(r/name).read_bytes()
    with (closure/name).open('xb') as f:f.write(data)
    saved[name]=hashlib.sha256(data).hexdigest()
observations={
 'observedAt':datetime.now(timezone.utc).isoformat(),
 'humanAuthorizedOneHadesFamilyLibraryDownload':True,
 'requestedMaximumDownloadSeconds':180,'temporaryClientLimitMbps':32,
 'guardReadyBeforeDownload':True,'clientDeadlineReset':False,
 'newNssSessionStarted':False,'checkpointCreated':False,'detachedStageStarted':False,
 'ecmOpened':False,'newControllerAttemptFileCreated':False,
 'defaultInspectBeforeLoad':{'gameCandidates':0,'bulkCandidates':0,'routerWrites':False},
 'actualDownloadObserved':{'libraryPercent':1,'networkMbps':31.9},
 'firstGameMatch':{'mode':'Deathmatch','mapGroup':'Defusal Group Alpha',
 'connectionResult':'The remote host closed the connection.',
 'nssWasStarted':False,'rootCauseEstablished':False},
 'secondGameMatch':{'sameGuardDeadline':True,'searchTimerObserved':'00:01',
 'finalConnectionOutcomeObserved':False},
 'gameHudJitterLossMissObserved':False,'actualGameAndBulkClassificationDuringLoadObserved':False,
 'factoryHardwareAcceptance':False,'humanExperienceAcceptance':False,
 'guardNaturalExactApplicationExitPassed':True,
 'guardDoesNotRestoreSteamSettingsOrPauseOnNextLaunch':True,
 'steamRelaunchForRestoration':{'initialToolResult':'launched app did not expose a targetable window: process:C:\\Program Files (x86)\\Steam\\steam.exe',
 'freshWindowThenObserved':True,'automaticDownloadResumptionObserved':True,
 'downloadPausedByUi':True,'lastDownloadedAmountShownMB':540.5,'libraryPercent':5,
 'measuredCumulativeDownloadDurationSeconds':None,
 'strictCumulative180SecondDownloadProofAvailable':False},
 'currentUiRestoration':{'steamLoggedInAndUsable':True,'hadesPaused':True,
 'networkBps':0,'diskBps':0,'steamDownloadLimitEnabled':False,
 'originalInactiveNumericLimitWasBlank':True,'inactiveNumericLimitClearedBeforeDisabling':True,
 'bitsPerSecondDisplayEnabled':True,'downloadsDuringGameplayEnabled':True,
 'downloadRegionPreserved':True,'cs2AndOwnedGuardProcessesRemaining':0,
 'downloadFragmentIntentionallyRetained':True,'hadesNotLaunched':True,
 'purchasedAnything':False,'uiSettingsRestoreConfirmed':True},
 'oldSteamStartupCrashes':{'exceptionCode':'c0000005','module':'ntdll.dll',
 'causeEstablished':False,'newStableSteamWindowConfirmed':True,
 'longTermSteamCrashFixClaim':False},
 'nextDownloadWindowRequiresSeparateUserAuthorization':True,
 'privateInputHashes':saved,'qualificationSourceCopiesExact':len(q['sourceManifest'])}
with (closure/'client-ui-observations.json').open('x',encoding='utf8') as f:
    json.dump(observations,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'qualificationSourceCopiesExact':len(q['sourceManifest']),
 'clientUiSettingsRestored':True,'factoryHardwareAcceptance':False,
 'cumulativeDownloadDurationNotMeasured':True,'privateInputsPreserved':len(saved)}))
