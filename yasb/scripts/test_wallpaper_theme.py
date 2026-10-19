"""Run with: python -m unittest discover -s scripts -p 'test_*.py'."""

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import wallpaper_theme as theme


class ThemeTests(unittest.TestCase):
    def test_variables_and_contrast(self):
        root = Path(__file__).resolve().parents[1] / "css/root.css"
        expected = set(re.findall(r"--([\w-]+):", root.read_text()))
        for colors in ([(0, 0, 0)], [(255, 255, 255)],
                       [(255, 0, 0), (0, 255, 0)], [(30, 30, 30)]):
            palette = theme.build_palette([(color, 1 / len(colors)) for color in colors])
            self.assertEqual(set(palette), expected)
            for name in ("text-primary", "text-secondary", "text-controls", "accent"):
                for background in ("bar-background", "media-background"):
                    self.assertGreaterEqual(theme.contrast(palette[name], palette[background]), 4.5)
            for foreground, background in (("on-accent", "accent"), ("badge-text", "badge-background")):
                self.assertGreaterEqual(theme.contrast(palette[foreground], palette[background]), 4.5)

    def test_preview_apply_restore_and_invalid_image(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            image = folder / "wallpaper con espacios.png"
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
            image.write_bytes(b"not an image")
            self.assertNotEqual(run(image, "--apply").returncode, 0)
            self.assertEqual(output.read_text(), "original")

    def test_transparent_image_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "transparent.png"
            Image.new("RGBA", (16, 16), (255, 0, 0, 0)).save(image)
            with self.assertRaises(ValueError):
                theme.extract(image, dict(sample_size=32, palette_size=12))

    def test_gray_wallpaper_stays_neutral(self):
        palette = theme.build_palette([((80, 80, 80), 1)])
        for color in palette.values():
            self.assertEqual(len(set(color)), 1)

    def test_accent_prefers_visible_color_over_tiny_saturated_detail(self):
        palette = theme.build_palette([((50, 100, 150), 0.99), ((255, 0, 0), 0.01)])
        self.assertGreater(palette["accent"][2], palette["accent"][0])
        self.assertNotEqual(palette["accent"], palette["accent-hover"])
        self.assertNotEqual(palette["text-controls"], palette["text-disabled"])

    def test_late_result_cannot_replace_newer_palette_or_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            settings = dict(output_css=folder / "root.css", backup_css=folder / "old.css")
            settings["output_css"].write_text("original")
            theme.apply_theme(settings, "newest", 20)
            theme.apply_theme(settings, "stale", 10)
            self.assertEqual(settings["output_css"].read_text(), "newest")
            self.assertEqual(settings["backup_css"].read_text(), "original")

    def test_invalid_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Path(directory) / "settings.json"
            settings.write_text("[]")
            with self.assertRaises(ValueError):
                theme.read_settings(settings)
            for value in (True, 16.5, "160", 0):
                settings.write_text(json.dumps(dict(sample_size=value, palette_size=12)))
                with self.assertRaises(ValueError):
                    theme.read_settings(settings)

    def test_concurrent_processes_keep_latest_result(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            output, backup = folder / "root.css", folder / "old.css"
            output.write_text("original")
            script = (
                "import sys; from pathlib import Path; "
                "sys.path.insert(0, sys.argv[1]); import wallpaper_theme as t; "
                "t.apply_theme(dict(output_css=Path(sys.argv[2]), "
                "backup_css=Path(sys.argv[3])), sys.argv[4], int(sys.argv[4]))"
            )
            processes = [subprocess.Popen([sys.executable, "-c", script,
                str(Path(theme.__file__).parent), str(output), str(backup), str(index)])
                for index in (8, 2, 6, 1, 7, 3, 5, 4)]
            for process in processes:
                self.assertEqual(process.wait(timeout=15), 0)
            self.assertEqual(output.read_text(), "8")
            self.assertIn(backup.read_text(), ["original", *map(str, range(1, 8))])

    def test_failed_replacement_preserves_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "root.css"
            output.write_text("original")
            with patch.object(theme.os, "replace", side_effect=PermissionError("locked")):
                with self.assertRaises(PermissionError):
                    theme.publish_css(output, "replacement")
            self.assertEqual(output.read_text(), "original")
            self.assertEqual(list(Path(directory).iterdir()), [output])


if __name__ == "__main__":
    unittest.main()
