import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import quoteswap


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.previous = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.temp.name
        self.addCleanup(self.restore_env)
        self.config, self.xkb, self.backup = quoteswap.paths()
        self.config.parent.mkdir(parents=True)
        self.original = 'hl.config({ input = { kb_layout = "gb", sensitivity = 0.4 } })\n'
        self.config.write_text(self.original)
        self.xkb.parent.mkdir(parents=True)
        self.xkb.write_text((HERE / "xkb/symbols/omarchy_quoteswap").read_text())

    def restore_env(self):
        if self.previous is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self.previous

    def test_enable_disable_uninstall(self):
        quoteswap.update(True)
        self.assertEqual(quoteswap.status(), "enabled")
        self.assertIn("sensitivity = 0.4", self.config.read_text())
        self.assertEqual(self.backup.read_text(), self.original)
        quoteswap.update(False)
        self.assertEqual(quoteswap.status(), "disabled")
        quoteswap.update(None)
        self.assertEqual(self.config.read_text(), self.original)

    def test_repeat_is_idempotent(self):
        quoteswap.update(True)
        first = self.config.read_text()
        quoteswap.update(True)
        self.assertEqual(self.config.read_text(), first)
        self.assertEqual(first.count(quoteswap.BEGIN), 1)

    def test_reject_broken_markers(self):
        self.config.write_text(quoteswap.BEGIN + "\n")
        with self.assertRaises(ValueError):
            quoteswap.update(True)

    def test_symbol_levels(self):
        data = self.xkb.read_text()
        self.assertIn('include "gb(basic)"', data)
        self.assertIn('[ 2, at, twosuperior, oneeighth ]', data)
        self.assertIn('[ apostrophe, quotedbl, dead_circumflex, dead_caron ]', data)


if __name__ == "__main__":
    unittest.main()
