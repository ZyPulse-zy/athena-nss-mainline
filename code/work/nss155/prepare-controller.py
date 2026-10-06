from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss154'
p=r/'epoch-driver.mjs';assert not p.exists()
s=(old/'epoch-driver-v3.mjs').read_text(encoding='utf-8').replace('work/nss154','work/nss155')
s=s.replace("from './session-binding-v3.mjs'","from './session-binding.mjs'").replace("from '../nss149/module-stage.mjs'","from './module-stage.mjs'")
s=s.replace('export async function runEpoch(continuityPath,onDetached){','export async function runEpoch(continuityPath,onDetached,expectedExit=false){')
anchor="  await waitStageUndo(context);assert.ok(latest,'No bounded-owner receipt');assert.equal(latest.error,undefined,latest.error);";assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n  if(expectedExit){assert.equal(latest.flowEligibilityExitCompleted,true);assert.equal(latest.terminalPairFirmwareZero,true);assert.equal(latest.automaticLifecycleEpochCompleted,false);assert.equal(latest.fastPathMeasurement.performanceComparison,false);assert.equal(latest.terminalInvalidation.ctExitInferredFromProjection,false);for(const k of ['moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'])assert.equal(latest[k],true,k);save('actual-accelerated-state-proof',validateAcceleratedState(latest.acceleratedState,selected));completed=true;return;}" )
s=s.replace("automaticLifecycleEpochCompleted:completed,gameQualityConclusion:false,errors:failures","automaticLifecycleEpochCompleted:completed&&!expectedExit,flowEligibilityExitCompleted:completed&&expectedExit,gameQualityConclusion:false,errors:failures")
p.write_text(s,encoding='utf-8',newline='')
# Only the explicitly owned application control flag is added; no process key,
# token, server address, pacing cap or independent deadline is changed.
p=r/'ssh-client.mjs';s=p.read_text(encoding='utf-8');anchor="if(x.tcpSourcePort!==undefined&&x.tcpSourcePort!==stats.tcpSourcePort)connectTcp(x.tcpSourcePort);";assert s.count(anchor)==1
s=s.replace(anchor,"if(x.closeTcp!==undefined){assert.equal(typeof x.closeTcp,'boolean');if(x.closeTcp&&stats.tcpConnected&&!stats.tcpClosingRequested)closeOwnedTcp();}"+anchor);p.write_text(s,encoding='utf-8',newline='')
print('Expected flow-exit receipts stay separate from normal20-second epochs; owned close control added.')
