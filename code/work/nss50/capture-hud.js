// Execute in node_repl with the initialized Sky API and a selected returned CS2 window.
// Pure observation: never focuses, clicks, types, or changes the router.
var hud50Fs = await import('node:fs/promises');
var hud50Dir = 'C:/Users/lishu/Documents/Codex/2026-09-30/referenced-chatgpt-conversation-this-is-an-2/work/nss50/hud-' + new Date().toISOString().replace(/\D/g,'').slice(0,17) + '-private';
await hud50Fs.mkdir(hud50Dir);
var hud50Frames = [];
var hud50Start = Date.now();
try {
 for (var hud50Index=0; hud50Index<45 && Date.now()-hud50Start<51000; hud50Index++) {
  var hud50Before = new Date().toISOString();
  csState = await sky.get_window_state({window:csWindow,include_screenshot:true,include_text:false});
  var hud50After = new Date().toISOString();
  var hud50Shot = csState.screenshots[0];
  if (!hud50Shot || !/^data:image\/jpeg;base64,/.test(hud50Shot.url)) throw new Error('Expected actual Sky JPEG screenshot');
  var hud50Name = String(hud50Index).padStart(3,'0')+'.jpg';
  await hud50Fs.writeFile(hud50Dir+'/'+hud50Name,Buffer.from(hud50Shot.url.slice(hud50Shot.url.indexOf(',')+1),'base64'),{flag:'wx'});
  hud50Frames.push({index:hud50Index,beforeAt:hud50Before,afterAt:hud50After,file:hud50Name,requestedWindowId:csState.window.id,width:hud50Shot.width,height:hud50Shot.height,source:'Actual Sky window capture',gameContentRequiresVisualVerification:true,foregroundOcclusionMustBeRejected:true,humanGameplay:false});
  await hud50Fs.writeFile(hud50Dir+'/frames.json',JSON.stringify(hud50Frames,null,2)+'\n');
  if (hud50Index===0) await hud50Fs.writeFile(hud50Dir+'/started.json',JSON.stringify({beforeAt:hud50Before,afterAt:hud50After,requestedWindowId:csState.window.id,firstFrameDurablySaved:true,readonly:true})+'\n',{flag:'wx'});
  await new Promise(resolve=>setTimeout(resolve,950));
 }
} finally {
 await hud50Fs.writeFile(hud50Dir+'/completion.json',JSON.stringify({startedAt:new Date(hud50Start).toISOString(),endedAt:new Date().toISOString(),frames:hud50Frames.length,readonly:true,routerAdmissionAllowed:false,captureLoopDoesNotInferZeroMetrics:true})+'\n',{flag:'wx'});
}
nodeRepl.write({directory:hud50Dir,frames:hud50Frames.length,firstFrame:hud50Frames[0],lastFrame:hud50Frames.at(-1)});
