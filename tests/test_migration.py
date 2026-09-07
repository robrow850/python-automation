import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import labtools
class Migration(unittest.TestCase):
    def test_plan_and_copy(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'source';dst=Path(t)/'destination';src.mkdir();(src/'sample').write_text('example')
            self.assertEqual(labtools.migrate_files(src,dst)['count'],1)
            self.assertFalse(dst.exists())
            self.assertTrue(labtools.migrate_files(src,dst,True)['verified'])
            self.assertEqual((src/'sample').read_text(),'example')
    def test_reject_existing_or_nested(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for dst in [root,root/'child']:
                with self.assertRaises(ValueError):labtools.migrate_files(root,dst,True)
if __name__=='__main__':unittest.main()
