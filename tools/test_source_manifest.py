"""Regression checks for revision handling and frozen-source integrity."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from source_manifest import latest_sources, verify_sources


def entry(path, data, revision=None):
    item = {'path': path, 'sha256': hashlib.sha256(data).hexdigest()}
    if revision is not None:
        item['revision'] = revision
    return item


class SourceManifestTests(unittest.TestCase):
    def test_current_controller_revision_preserves_history(self):
        old = entry('code/controller/core.lua', b'old')
        new = entry('code/controller/core.lua', b'new', 'reviewed-revision')
        manifest = {'sources': [old, new]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / new['path']
            source.parent.mkdir(parents=True)
            source.write_bytes(b'new')
            self.assertEqual(verify_sources(root, manifest), 1)
        self.assertEqual(manifest['sources'], [old, new])

    def test_current_bytes_still_need_the_latest_hash(self):
        manifest = {'sources': [entry('code/controller/core.lua', b'expected')]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / manifest['sources'][0]['path']
            source.parent.mkdir(parents=True)
            source.write_bytes(b'changed-without-a-record')
            with self.assertRaises(AssertionError):
                verify_sources(root, manifest)

    def test_frozen_source_cannot_be_revised(self):
        path = 'code/work/frozen/core.lua'
        with self.assertRaises(AssertionError):
            latest_sources({'sources': [entry(path, b'old'), entry(path, b'new', 'revision')]})

    def test_controller_change_needs_a_named_revision(self):
        path = 'code/controller/core.lua'
        with self.assertRaises(AssertionError):
            latest_sources({'sources': [entry(path, b'old'), entry(path, b'new')]})


if __name__ == '__main__':
    unittest.main()
