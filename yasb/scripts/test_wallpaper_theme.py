"""Run with: python -m unittest discover -s scripts -p 'test_*.py'."""

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import wallpaper_theme as theme


class ThemeTests(unittest.TestCase):
    def test_variables_and_contrast(self):
        root = Path(__file__).resolve().parents[1] / "css/root.css"
        expected = set(re.findall(r"--([\w-]+):", root.read_text()))
        for colors in ([(0, 0, 0)], [(255, 255, 255)],
                       [(255, 0, 0), (0, 255, 0)], [(30, 30, 30)]):
            palette = theme.build_palette(colors)
            self.assertEqual(set(palette), expected)
            for name in ("text-primary", "text-secondary", "text-controls", "accent"):
                self.assertGreaterEqual(theme.contrast(palette[name], palette["bar-background"]), 4.5)
            for foreground, background in (("on-accent", "accent"), ("badge-text", "badge-background")):
                self.assertGreaterEqual(theme.contrast(palette[foreground], palette[background]), 4.5)

    def test_preview_apply_restore_and_invalid_image(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            image = folder / "wallpaper.png"
            Image.new("RGB", (32, 32), (30, 100, 180)).save(image)
            output = folder / "root.css"
            output.write_text("original", encoding="utf-8")
            settings = folder / "settings.json"
            settings.write_text(json.dumps(dict(mode="dark", sample_size=32,
                palette_size=12, fixed_accent=None, output_css="root.css",
                backup_css="backup.css")), encoding="utf-8")
            command = [sys.executable, str(Path(theme.__file__).resolve()),
                       "--settings", str(settings)]

            def run(*args):
                return subprocess.run([*command, *map(str, args)], capture_output=True, text=True)

            self.assertEqual(run(image).returncode, 0)
            self.assertEqual(output.read_text(), "original")
            self.assertEqual(run(image, "--apply").returncode, 0)
            self.assertIn("--accent:", output.read_text())
            self.assertEqual((folder / "backup.css").read_text(), "original")
            self.assertEqual(run(image, "--apply").returncode, 0)
            self.assertEqual((folder / "backup.css").read_text(), "original")
            self.assertEqual(run("--restore").returncode, 0)
            self.assertEqual(output.read_text(), "original")
            self.assertNotEqual(run(folder / "missing.png", "--apply").returncode, 0)
            self.assertEqual(output.read_text(), "original")

    def test_transparent_image_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "transparent.png"
            Image.new("RGBA", (16, 16), (255, 0, 0, 0)).save(image)
            with self.assertRaises(ValueError):
                theme.extract(image, dict(sample_size=32, palette_size=12))


if __name__ == "__main__":
    unittest.main()
