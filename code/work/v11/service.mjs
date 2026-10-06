import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {verifyPreparation} from './session-binding.mjs';
import {selectRealPair} from '../nss39/pair-policy.mjs';
import {runService} from './service-engine.mjs';

const workspace = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
process.chdir(workspace);
const base = 'work/v11/runtime', active = base + '/active.json';
const statusFile = base + '/status.json';
fs.mkdirSync(base, {recursive: true});
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function atomicJson(file, value) {
  const temporary = file + '.' + crypto.randomBytes(4).toString('hex') + '.tmp';
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n', {flag: 'wx'});
  fs.renameSync(temporary, file);
}
function ownRun(id) {
  assert.match(id, /^[a-f0-9]{32}$/);
  return base + '/run-' + id;
}
function describe() {
  const result = fs.existsSync(statusFile) ? read(statusFile) : {phase: 'NOT_STARTED'};
  return {...result, active: fs.existsSync(active),
    stopPending: fs.existsSync(active) && fs.existsSync(ownRun(read(active).id) + '/stop-request.json'),
    permanentNssDeployment: false, maximumSessionsPerStart: 1};
}
async function child(file, args, dir, name, timeoutMs) {
  const p = spawn(process.execPath, [file, ...args], {windowsHide: true, stdio: ['ignore', 'pipe', 'pipe']});
  let stdout = '', stderr = '', limitExceeded = false, timedOut = false;
  function append(key, bytes) {
    if (Buffer.byteLength(stdout) + Buffer.byteLength(stderr) + bytes.length > 1048576) {
      limitExceeded = true; p.kill(); return;
    }
    if (key === 'stdout') stdout += bytes.toString(); else stderr += bytes.toString();
  }
  p.stdout.on('data', b => append('stdout', b)); p.stderr.on('data', b => append('stderr', b));
  const timer = setTimeout(() => {timedOut = true; p.kill();}, timeoutMs);
  let code, error;
  try {code = await new Promise((resolve, reject) => {p.once('error', reject); p.once('close', resolve);});}
  catch (e) {error = String(e);} finally {clearTimeout(timer);}
  fs.writeFileSync(dir + '/' + name + '-private.json', JSON.stringify({file, args, code, error,
    stdout, stderr, timedOut, limitExceeded}, null, 2) + '\n', {flag: 'wx'});
  assert.ok(!error && !timedOut && !limitExceeded, 'Child failed; original output retained privately');
  const output = JSON.parse(stdout.trim().split(/\r?\n/).at(-1));
  if (name.startsWith('inspect-')) assert.equal(code, 0, 'Read-only discovery failed');
  else assert.ok(code === 0 || (output.passed === false && output.recoveryVerified));
  return output;
}
async function worker(id) {
  const dir = ownRun(id), owner = read(active);
  assert.equal(owner.id, id); assert.equal(owner.pid, process.pid);
  verifyPreparation();
  let last = {id, workerPid: process.pid, phase: 'STARTING', finished: false};
  const save = patch => {
    assert.equal(read(active).id, id, 'Service ownership changed');
    last = {...last, ...patch, updatedAt: new Date().toISOString()};
    atomicJson(dir + '/status.json', last); atomicJson(statusFile, last); return last;
  };
  let index = 0;
  try {
    const result = await runService({deadline: owner.deadline,
      stopped: () => fs.existsSync(dir + '/stop-request.json'), save, sleep,
      inspect: async () => {
        verifyPreparation();
        const observation = await child('work/v11/session.mjs', ['inspect'], dir, 'inspect-' + index++, 45000);
        const candidates = read('work/v11/real-candidates-private.json');
        const pairs = selectRealPair(candidates);
        return {ready: pairs.length > 0, wan: pairs[0]?.g.identity.wan,
          observedAt: observation.observedAt, gameFlows: observation.actualGameCandidates,
          bulkFlows: observation.actualBulkCandidates, routerWrites: observation.routerWrites,
          nssPermissionGranted: observation.nssPermissionGranted};
      },
      execute: async wan => {
        verifyPreparation();
        return child('work/v11/session.mjs', ['session', dir + '/stop-request.json', String(wan)],
          dir, 'session', 210000);
      }});
    fs.writeFileSync(dir + '/result.json', JSON.stringify(result, null, 2) + '\n', {flag: 'wx'});
    // Unconfirmed restoration deliberately holds the local admission lock.
    if (result.phase !== 'RESTORATION_UNCONFIRMED') {
      assert.equal(read(active).id, id); fs.unlinkSync(active);
    }
  } catch (e) {
    fs.writeFileSync(dir + '/worker-failure-private.json', JSON.stringify({error: String(e)}, null, 2) + '\n', {flag: 'wx'});
    save({phase: 'WORKER_FAILED_ADMISSION_LOCK_RETAINED', finished: true});
  }
}

const action = process.argv[2] ?? 'status';
assert.ok(['start', 'stop', 'status', 'worker'].includes(action));
if (action === 'worker') {
  // Launcher records child ownership before the child starts inspecting anything.
  await sleep(150); await worker(process.argv[3]);
} else if (action === 'status') console.log(JSON.stringify(describe()));
else if (action === 'stop') {
  if (fs.existsSync(active)) {
    const owner = read(active), target = ownRun(owner.id) + '/stop-request.json';
    if (!fs.existsSync(target)) fs.writeFileSync(target, JSON.stringify({id: owner.id,
      requestedAt: new Date().toISOString(), stopNewAdmissions: true}) + '\n', {flag: 'wx'});
  }
  console.log(JSON.stringify(describe()));
} else {
  verifyPreparation();
  if (fs.existsSync(active)) throw Error('An owned invocation already exists; inspect status instead of launching a duplicate');
  const id = crypto.randomBytes(16).toString('hex'), dir = ownRun(id);
  fs.mkdirSync(dir);
  const owner = {id, startedAt: new Date().toISOString(), deadline: Date.now() + 600000,
    oneSessionPerEnable: true, workspace, pid: null};
  fs.writeFileSync(active, JSON.stringify(owner) + '\n', {flag: 'wx'});
  let p;
  try {
    p = spawn(process.execPath, ['work/v11/service.mjs', 'worker', id],
      {detached: true, windowsHide: true, stdio: 'ignore'});
    assert.ok(Number.isInteger(p.pid)); owner.pid = p.pid; atomicJson(active, owner);
    atomicJson(statusFile, {id, workerPid: p.pid, phase: 'STARTING', finished: false,
      updatedAt: new Date().toISOString(), permanentNssDeployment: false});
    p.unref();
  } catch (error) {
    if (read(active).id === id && !Number.isInteger(owner.pid)) fs.unlinkSync(active);
    throw error;
  }
  console.log(JSON.stringify(describe()));
}
