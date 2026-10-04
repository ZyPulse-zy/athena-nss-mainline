// Execute only in the initialized Sky node_repl. Read-only evidence capture.
// Covers the controller's preparation as well as all three forwarding phases.
var hud50LongFs = await import('node:fs/promises');
var hud50LongDir = 'C:/Users/lishu/Documents/Codex/2026-09-30/referenced-chatgpt-conversation-this-is-an-2/work/nss50/hud-' + new Date().toISOString().replace(/\D/g,'').slice(0,17) + '-private';
await hud50LongFs.mkdir(hud50LongDir);
var hud50LongFrames = [];
var hud50LongStart = Date.now();
try {
 for (var hud50LongIndex=0; hud50LongIndex<90 && Date.now()-hud50LongStart<96000; hud50LongIndex++) {
  var hud50LongBefore = new Date().toISOString();
  csState = await sky.get_window_state({window:csWindow,include_screenshot:true,include_text:false});
  var hud50LongAfter = new Date().toISOString();
  var hud50LongShot = csState.screenshots[0];
  if (!hud50LongShot || !/^data:image\/jpeg;base64,/.test(hud50LongShot.url)) throw new Error('Expected actual Sky JPEG screenshot');
  var hud50LongName = String(hud50LongIndex).padStart(3,'0')+'.jpg';
  await hud50LongFs.writeFile(hud50LongDir+'/'+hud50LongName,Buffer.from(hud50LongShot.url.slice(hud50LongShot.url.indexOf(',')+1),'base64'),{flag:'wx'});
  hud50LongFrames.push({index:hud50LongIndex,beforeAt:hud50LongBefore,afterAt:hud50LongAfter,file:hud50LongName,requestedWindowId:csState.window.id,width:hud50LongShot.width,height:hud50LongShot.height,source:'Actual Sky window capture',gameContentRequiresVisualVerification:true,foregroundOcclusionMustBeRejected:true,humanGameplay:false});
  await hud50LongFs.writeFile(hud50LongDir+'/frames.json',JSON.stringify(hud50LongFrames,null,2)+'\n');
  if (hud50LongIndex===0) await hud50LongFs.writeFile(hud50LongDir+'/started.json',JSON.stringify({beforeAt:hud50LongBefore,afterAt:hud50LongAfter,requestedWindowId:csState.window.id,firstFrameDurablySaved:true,readonly:true})+'\n',{flag:'wx'});
  await new Promise(resolve=>setTimeout(resolve,950));
 }
} finally {
 await hud50LongFs.writeFile(hud50LongDir+'/completion.json',JSON.stringify({startedAt:new Date(hud50LongStart).toISOString(),endedAt:new Date().toISOString(),frames:hud50LongFrames.length,readonly:true,routerAdmissionAllowed:false,captureLoopDoesNotInferZeroMetrics:true})+'\n',{flag:'wx'});
}
nodeRepl.write({directory:hud50LongDir,frames:hud50LongFrames.length,firstFrame:hud50LongFrames[0],lastFrame:hud50LongFrames.at(-1)});
