"""Opt-in Java production runner never opens the original save for writing."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from tools.run_hammer_probe import run, sha256


class RunnerTests(unittest.TestCase):
    def test_missing_files_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'must both exist'):
            run('missing.jar', 'missing.fsg')

    def test_compilation_failure_keeps_original_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            jar = Path(directory) / 'freecol.jar'
            save = Path(directory) / 'game.fsg'
            jar.write_bytes(b'jar-placeholder')
            save.write_bytes(b'example-save-bytes')
            digest = sha256(save)
            with patch('tools.run_hammer_probe.subprocess.run',
                       return_value=SimpleNamespace(returncode=1, stderr='missing dependency')):
                with self.assertRaisesRegex(RuntimeError, 'compilation failed'):
                    run(jar, save)
            self.assertEqual(sha256(save), digest)


if __name__ == '__main__':
    unittest.main()
