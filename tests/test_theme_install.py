"""Theme installation from an archive: destination folder name and copy.

Run with:  python3 -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.grub_manager import theme_install_name  # noqa: E402


class ThemeInstallNameTests(unittest.TestCase):
    def test_theme_txt_inside_a_folder_uses_the_folder_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = os.path.join(tmpdir, "Vimix")
            self.assertEqual(theme_install_name(folder, tmpdir, "/home/u/vimix-1.0.tar.gz"), "Vimix")

    def test_theme_txt_at_the_top_uses_the_archive_name(self):
        # os.walk() yields the extraction directory itself as root; its
        # basename is the random temporary name, never ''.
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "theme.txt").touch()
            root = next(r for r, _d, files in os.walk(tmpdir) if "theme.txt" in files)
            for archive, name in (("/x/Tela.tar.gz", "Tela"), ("/x/Tela.tar.xz", "Tela"),
                                  ("/x/Tela.tar.bz2", "Tela"), ("/x/Tela.tgz", "Tela"),
                                  ("/x/Tela.zip", "Tela"), ("/x/my.theme.zip", "my.theme")):
                with self.subTest(archive=archive):
                    self.assertEqual(theme_install_name(root, tmpdir, archive), name)


class ThemeCopyTests(unittest.TestCase):
    def test_reinstall_replaces_instead_of_nesting(self):
        # Same cp options as AppearanceView._install_theme_from_archive.
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp, "src", "Tela")
            src.mkdir(parents=True)
            (src / "theme.txt").write_text("v2\n")
            dest = Path(tmp, "themes", "Tela")
            dest.mkdir(parents=True)
            (dest / "theme.txt").write_text("v1\n")
            subprocess.run(["cp", "-rT", str(src), str(dest)], check=True)
            self.assertFalse((dest / "Tela").exists())
            self.assertEqual((dest / "theme.txt").read_text(), "v2\n")

    def test_view_uses_the_helper_and_cp_t(self):
        source = (ROOT / "ui/views/appearance_view.py").read_text(encoding="utf-8")
        self.assertIn("theme_install_name(theme_folder, tmpdir, archive_path)", source)
        self.assertIn("['pkexec', 'cp', '-rT', theme_folder, dest_path]", source)


if __name__ == "__main__":
    unittest.main()
