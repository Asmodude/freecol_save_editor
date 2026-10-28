"""H1: report is bound to bytes opened by Qt, not a later disk replacement."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from save_document import SaveDocument
from qt_hammer_probe import HammerProbeError, read_verified_report


def archive(path, turn):
    with zipfile.ZipFile(path, 'w') as zipfile_handle:
        zipfile_handle.writestr('savegame.xml',
            f'<savedGame><game turn="{turn}">'
            '<player id="player:1" username="Denmark"/>'
            '<map><tile x="1" y="1"><colony id="colony:1" '
            'name="Taphus" owner="player:1"/></tile></map>'
            '</game></savedGame>')


class LoadedSnapshotBindingTests(unittest.TestCase):
    def test_replaced_file_is_not_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            save = Path(tmp) / 'save.fsg'
            report = Path(tmp) / 'report.json'
            archive(save, 12)
            document = SaveDocument.load(save)
            original_digest = document.source_sha256
            original_report = {
                'format': 'FREECOL_HAMMERS_REPORT_V1',
                'save_sha256': original_digest,
                'probe_output': 'FREECOL_HAMMERS_V1\tcolony_id\towner_id\tgross\tnet\n'
                                'colony:1\tplayer:1\t12\t12\n',
            }
            archive(save, 13)
            self.assertNotEqual(hashlib.sha256(save.read_bytes()).hexdigest(), original_digest)
            report.write_text(json.dumps(original_report), encoding='utf-8')
            self.assertEqual(read_verified_report(report, document)['colony:1'].gross, 12)
            original_report['save_sha256'] = hashlib.sha256(save.read_bytes()).hexdigest()
            report.write_text(json.dumps(original_report), encoding='utf-8')
            with self.assertRaisesRegex(HammerProbeError, 'different save'):
                read_verified_report(report, document)


if __name__ == '__main__':
    unittest.main()
