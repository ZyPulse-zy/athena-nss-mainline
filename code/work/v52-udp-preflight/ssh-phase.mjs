import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';

const stages = Object.freeze([
  ['TCP_ESTABLISHED', /Connection established\./],
  ['BANNER_RECEIVED', /Remote protocol version /],
  ['KEX_INIT_RECEIVED', /SSH2_MSG_KEXINIT received/],
  ['KEX_REPLY_PENDING', /expecting SSH2_MSG_KEX_ECDH_REPLY/],
  ['KEX_COMPLETE', /SSH2_MSG_NEWKEYS received/],
  ['AUTHENTICATED', /Authenticated to /],
  ['COMMAND_SENT', /Sending command: /],
]);

export function createPhaseTracker({slot, attempt, ownerPid, elapsed}) {
  assert.ok(['tcp', 'tcp2', 'tcp3', 'tcp4'].includes(slot));
  assert.ok(Number.isInteger(attempt) && attempt >= 1 && attempt <= 8);
  let phase = 'SPAWNED', rank = -1, remainder = '', rawTail = '', rawBytes = 0, payloadBytes = 0;
  const events = [{phase, elapsed: elapsed()}];
  function line(value) {
    for (let i = 0; i < stages.length; i++) {
      if (i > rank && stages[i][1].test(value)) {
        rank = i; phase = stages[i][0]; events.push({phase, elapsed: elapsed()});
      }
    }
    return /^debug[123]: /.test(value) ? '' : value + '\n';
  }
  return {
    consume(chunk) {
      const value = String(chunk); rawBytes += Buffer.byteLength(value);
      rawTail = Buffer.from(rawTail + value).subarray(-8192).toString();
      remainder += value; let nonDebug = '', end;
      while ((end = remainder.indexOf('\n')) >= 0) {
        nonDebug += line(remainder.slice(0, end).replace(/\r$/, ''));
        remainder = remainder.slice(end + 1);
      }
      assert.ok(Buffer.byteLength(remainder) <= 8192, 'SSH diagnostic line ceiling');
      return nonDebug;
    },
    payload(bytes) {
      assert.ok(Number.isInteger(bytes) && bytes > 0); payloadBytes += bytes;
      if (phase !== 'PAYLOAD_RECEIVED') {
        rank = stages.length; phase = 'PAYLOAD_RECEIVED'; events.push({phase, elapsed: elapsed()});
      }
    },
    snapshot(reason, code = null) {
      return {slot, attempt, ownerPid: ownerPid(), reason, code, phase,
        elapsed: elapsed(), payloadBytes, events: events.map(x => ({...x})),
        rawStderrTail: rawTail, rawStderrBytes: rawBytes,
        rawTailTruncated: rawBytes > 8192, inferenceIsOnlyObservedSshPhase: true};
    },
  };
}

export function createSshPhaseRecorder(options) {
  const target = path.join(options.dir, 'transport-attempts-private.jsonl');
  const tracker = createPhaseTracker(options);
  return {
    consume: tracker.consume,
    payload: tracker.payload,
    snapshot(reason, code = null) {
      const record = tracker.snapshot(reason, code), bytes = JSON.stringify(record) + '\n';
      const prior = fs.existsSync(target) ? fs.statSync(target).size : 0;
      assert.ok(prior + Buffer.byteLength(bytes) <= 1048576, 'Owned diagnostic record ceiling');
      fs.appendFileSync(target, bytes, {flag: prior ? 'a' : 'wx'});
      return record;
    },
  };
}

export function instrumentNativeClient(source) {
  const replace = (before, after) => {
    assert.equal(source.split(before).length, 2, 'Exact native diagnostic patch required');
    source = source.replace(before, after);
  };
  source = "import{createSshPhaseRecorder}from'../v52-udp-preflight/ssh-phase.mjs';\n" + source;
  replace("const p=spawn(sshExe,['-o','BatchMode=yes'",
    "const attemptTrace=createSshPhaseRecorder({dir,slot,attempt,ownerPid:()=>p.pid,elapsed:()=>(performance.now()-began)/1000});const p=spawn(sshExe,['-v','-o','BatchMode=yes'");
  replace("if(p===children.get(slot)&&!s.connected&&!ended)retryAcquisition(slot,p,'No first payload within 8 seconds');",
    "if(p===children.get(slot)&&!s.connected&&!ended){attemptTrace.snapshot('no-first-payload');retryAcquisition(slot,p,'No first payload within 8 seconds');}");
  replace("clearTimeout(acquisitionTimers.get(slot));s.connected=true;s.bytes+=b.length;",
    "clearTimeout(acquisitionTimers.get(slot));attemptTrace.payload(b.length);s.connected=true;s.bytes+=b.length;");
  replace("p.stderr.on('data',b=>{stderr+=b;",
    "p.stderr.on('data',b=>{stderr+=attemptTrace.consume(b);");
  replace("p.on('close',code=>{if(p!==children.get(slot)",
    "p.on('close',code=>{attemptTrace.snapshot('child-close',code);if(p!==children.get(slot)");
  return source;
}
