"""Check the real client runner with a local transport fixture; no router I/O."""
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'code/controller/wifi-observe.mjs'
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'Node.js is required')
class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='athena-wifi-transport-')
        self.folder = pathlib.Path(self.temp.name)
        self.transport = self.folder / 'transport.mjs'
        self.transport.write_text("""import fs from 'node:fs';
export async function connect(){
 fs.writeFileSync('connected','yes');
 return {run(){throw Error('Exec payload must not be used');},
  async runStdin(command,source){
   if(command!=='timeout -k 2 50 lua -')throw Error('Wrong command');
   if(!source.includes("package.loaded['athena.wifi']")||!source.includes("arg={[0]='-',[1]='5'}"))throw Error('Source missing');
   fs.writeFileSync('stdin-proof.json',JSON.stringify({command,bytes:source.length}));
   return {code:0,stderr:'',stdout:JSON.stringify({raw:{privateIdentity:'02:11:22:33:44:55'},report:{elapsedSeconds:5,queries:[{seconds:0.01}],topology:{start:'ok'}}})};
  },close(){fs.writeFileSync('closed','yes');}};
}
""", encoding='utf8')

    def tearDown(self):
        self.temp.cleanup()

    def run_observer(self, name='capture', seconds='5'):
        return subprocess.run([NODE, str(RUNNER), '--transport', str(self.transport),
                               '--transport-cwd', str(self.folder), '--private-dir',
                               str(self.folder / name), '--seconds', seconds],
                              capture_output=True, text=True, timeout=15)

    def test_stdin_private_capture_and_close(self):
        result = self.run_observer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('02:11:22:33:44:55', result.stdout)
        self.assertTrue((self.folder / 'closed').is_file())
        capture = self.folder / 'capture'
        self.assertIn('02:11:22:33:44:55', (capture / 'raw-private.json').read_text())
        summary = json.loads((capture / 'summary.json').read_text())
        self.assertTrue(summary['streamedWithoutInstallation'])
        self.assertEqual(len(summary['sourceFiles']), 3)
        self.assertFalse(json.loads(result.stdout)['installed'])
        if not __import__('os').name == 'nt':
            self.assertEqual(capture.stat().st_mode & 0o777, 0o700)
            self.assertEqual((capture / 'raw-private.json').stat().st_mode & 0o777, 0o600)

    def test_bad_duration_before_connection_or_directory(self):
        result = self.run_observer(seconds='4')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.folder / 'connected').exists())
        self.assertFalse((self.folder / 'capture').exists())

    def test_existing_capture_is_never_overwritten(self):
        (self.folder / 'capture').mkdir()
        result = self.run_observer()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.folder / 'connected').exists())

    def test_long_exec_request_refused_before_observation(self):
        self.transport.write_text("""import fs from 'node:fs';
export async function connect(){return {run(){fs.writeFileSync('executed','yes');throw Error('Unexpected execution');},close(){fs.writeFileSync('closed','yes');}};}
""", encoding='utf8')
        result = self.run_observer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('runStdin', result.stderr)
        self.assertFalse((self.folder / 'executed').exists())
        self.assertTrue((self.folder / 'closed').exists())


if __name__ == '__main__':
    unittest.main()
