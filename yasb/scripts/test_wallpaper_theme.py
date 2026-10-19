"""Run with: python -m unittest discover -s scripts -p 'test_*.py'."""

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


class ThemeTests(unittest.TestCase):
    def test_preview_apply_restore_and_invalid_image(self):
        script = Path(__file__).with_name("wallpaper_theme.py")
        root = script.parents[1] / "css/root.css"
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            image = folder / "wallpaper con espacios.png"
            Image.new("RGB", (32, 32), (30, 100, 180)).save(image)
            output = folder / "root.css"
            output.write_text("original", encoding="utf-8")
            settings = folder / "settings.json"
            settings.write_text(json.dumps(dict(sample_size=32,
                palette_size=12, fixed_accent=None, output_css="root.css",
                backup_css="backup.css")), encoding="utf-8")
            command = [sys.executable, str(script.resolve()),
                       "--settings", str(settings)]

            def run(*args):
                return subprocess.run([*command, *map(str, args)], capture_output=True,
                                      text=True, timeout=15)

            self.assertEqual(run(image).returncode, 0)
            self.assertEqual(output.read_text(), "original")
            self.assertEqual(run(image, "--apply").returncode, 0)
            generated = output.read_text()
            self.assertEqual(set(re.findall(r"--([\w-]+):", generated)),
                             set(re.findall(r"--([\w-]+):", root.read_text())))
            self.assertEqual((folder / "backup.css").read_text(), "original")
            self.assertEqual(run(image, "--apply").returncode, 0)
            self.assertEqual((folder / "backup.css").read_text(), "original")
            self.assertEqual(run("--restore").returncode, 0)
            self.assertEqual(output.read_text(), "original")
            self.assertNotEqual(run(folder / "missing.png", "--apply").returncode, 0)
            self.assertEqual(output.read_text(), "original")
            image.write_bytes(b"not an image")
            self.assertNotEqual(run(image, "--apply").returncode, 0)
            self.assertEqual(output.read_text(), "original")


if __name__ == "__main__":
    unittest.main()
