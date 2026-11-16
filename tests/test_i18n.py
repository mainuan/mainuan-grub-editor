"""i18n smoke tests: gettext lookup follows LANGUAGE/LC_ALL/LC_MESSAGES/LANG.

Run with:  python3 -m unittest discover -s tests -v
The catalogs are compiled into a temporary directory first, so a checkout
without .mo files is tested exactly like the installed package.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROBE = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
from core import i18n_manager as m
mgr = m.get_i18n_manager()
out = {"save": m._("Save"), "boot": m._("Boot Entries"), "lang": m.get_current_language(),
       "fmt": m._("Entry '{}' not found in {}").format("x", "y"),
       "name": m._(m.N_("Mainuan GRUB Editor")), "available": sorted(mgr.get_available_languages())}
if len(sys.argv) > 2:
    out["set"] = m.set_language(sys.argv[2]); out["after_set"] = m._("Save")
print(json.dumps(out))
'''

GTK_PROBE = r'''
import sys
sys.path.insert(0, sys.argv[1])
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
if not Gtk.init_check(sys.argv)[0]:
    print("NO-DISPLAY"); sys.exit(0)
from ui.views.general_view import GeneralView
view = GeneralView.__new__(GeneralView)
Gtk.Box.__init__(view, orientation=Gtk.Orientation.VERTICAL)
view._create_ui()                      # real widget code, no window is shown
frames = []
def walk(w):
    if isinstance(w, Gtk.Frame): frames.append(w.get_label())
    if isinstance(w, Gtk.Container): w.foreach(walk)
walk(view)
print(frames[0])
'''


class TranslationLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.localedir = cls._tmp.name
        subprocess.run([str(ROOT / "po/i18n.sh"), "compile", cls.localedir], check=True)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def env(self, **values):
        env = {k: v for k, v in os.environ.items() if k not in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")}
        env["MAINUAN_GRUB_EDITOR_LOCALEDIR"] = self.localedir
        env.update(values)
        return env

    def probe(self, *extra, **values):
        result = subprocess.run([sys.executable, "-c", PROBE, str(ROOT), *extra], env=self.env(**values),
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_brazilian_portuguese(self):
        out = self.probe(LANGUAGE="pt_BR", LANG="pt_BR.UTF-8")
        self.assertEqual((out["save"], out["boot"], out["lang"]), ("Salvar", "Entradas de inicialização", "pt_BR"))
        self.assertEqual(out["fmt"], "Entrada 'x' não encontrada em y")

    def test_lang_alone_selects_pt_br(self):
        self.assertEqual(self.probe(LANG="pt_BR.UTF-8")["save"], "Salvar")

    def test_european_portuguese_is_separate(self):
        out = self.probe(LANGUAGE="pt_PT:pt")
        self.assertEqual((out["save"], out["boot"], out["lang"]), ("Guardar", "Entradas de Arranque", "pt"))

    def test_language_list_order_is_respected(self):
        self.assertEqual(self.probe(LANGUAGE="ja:pt_BR:en")["save"], "Salvar")
        self.assertEqual(self.probe(LANGUAGE="es_AR:pt_BR", LANG="pt_BR.UTF-8")["lang"], "es")

    def test_unknown_language_falls_back_to_english_msgid(self):
        for values in ({"LANGUAGE": "ja"}, {"LANGUAGE": "en"}, {"LC_ALL": "C"}, {"LANG": "nl_NL.UTF-8"}):
            with self.subTest(**values):
                out = self.probe(**values)
                self.assertEqual((out["save"], out["name"], out["lang"]), ("Save", "Mainuan GRUB Editor", "en"))

    def test_lc_all_overrides_lang(self):
        self.assertEqual(self.probe(LC_ALL="fr_FR.UTF-8", LANG="pt_BR.UTF-8")["lang"], "fr")

    def test_public_api_set_language_and_available(self):
        out = self.probe("pt_BR", LANGUAGE="en")
        self.assertTrue(out["set"])
        self.assertEqual(out["after_set"], "Salvar")
        self.assertIn("pt_BR", out["available"])
        self.assertIn("en", out["available"])
        self.assertFalse(self.probe("xx", LANGUAGE="en")["set"])

    def test_gtk_widgets_show_translation_when_display_available(self):
        result = subprocess.run([sys.executable, "-c", GTK_PROBE, str(ROOT)],
                                env=self.env(LANGUAGE="pt_BR", LANG="pt_BR.UTF-8"),
                                capture_output=True, text=True, timeout=30)
        if result.returncode != 0 and "No module named 'gi'" in result.stderr:
            self.skipTest("PyGObject not installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        if result.stdout.strip() == "NO-DISPLAY":
            self.skipTest("no display available")
        self.assertEqual(result.stdout.strip(), "Configuração de inicialização")


class CatalogTests(unittest.TestCase):
    def test_pt_br_is_complete(self):
        stats = subprocess.run(["msgfmt", "--statistics", "-o", os.devnull,
                                str(ROOT / "locale/pt_BR/LC_MESSAGES/mainuan-grub-editor.po")],
                               capture_output=True, text=True, env={**os.environ, "LC_ALL": "C"}, check=True)
        self.assertNotIn("untranslated", stats.stderr)
        self.assertNotIn("fuzzy", stats.stderr)

    def test_no_fixed_language_list(self):
        source = (ROOT / "core/i18n_manager.py").read_text()
        self.assertNotIn("SUPPORTED_LANGUAGES", source)
        self.assertNotIn("FALLBACK_CHAIN", source)


if __name__ == "__main__":
    unittest.main()
