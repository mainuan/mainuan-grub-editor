"""
Internationalization (i18n) manager for Mainuan GRUB Editor.

Source strings (msgid) are English. The catalog is chosen by the standard
gettext lookup, which honours LANGUAGE, LC_ALL, LC_MESSAGES and LANG in this
order (e.g. LANGUAGE=pt_BR:en, LANG=es_AR.UTF-8 -> es). Any language with a
compiled catalog works; when none matches, the English msgid is shown.
"""

import gettext
import os
import sys
from pathlib import Path
from typing import Dict, Optional

DOMAIN = 'mainuan-grub-editor'
# Optional override, mainly for running from a source tree or tests.
LOCALEDIR_ENV = 'MAINUAN_GRUB_EDITOR_LOCALEDIR'

# Display names only; they never restrict which languages can be used.
LANGUAGE_NAMES = {
    'de': 'Deutsch',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'pt': 'Português',
    'pt_BR': 'Português (Brasil)',
    'ro': 'Română',
    'ru': 'Русский',
}


def default_locale_dir() -> Optional[str]:
    """Locate compiled catalogs.

    1. $MAINUAN_GRUB_EDITOR_LOCALEDIR, when set;
    2. <source tree>/locale when it holds compiled .mo files
       (``po/i18n.sh compile locale`` in a checkout);
    3. None: the system directory (/usr/share/locale) used by the package.
    """
    override = os.environ.get(LOCALEDIR_ENV)
    if override:
        return override
    source = Path(__file__).resolve().parent.parent / 'locale'
    if any(source.glob(f'*/LC_MESSAGES/{DOMAIN}.mo')):
        return str(source)
    return None


def _language_of(translation) -> str:
    """Language code of a loaded catalog ('en' for the English source)."""
    if isinstance(translation, gettext.GNUTranslations):
        lang = translation.info().get('language', '').strip()
        if lang:
            return lang.replace('-', '_')
    return 'en'


class I18nManager:
    """
    Thin wrapper around gettext.translation(domain, localedir, fallback=True).
    Keeps the historical API used by the rest of the application.
    """

    def __init__(self, locale_dir: Optional[str] = None, domain: str = DOMAIN):
        """
        Initialize the i18n manager.

        Args:
            locale_dir: Directory with <lang>/LC_MESSAGES/<domain>.mo files;
                None selects default_locale_dir().
            domain: Translation domain name
        """
        if locale_dir is None:
            locale_dir = default_locale_dir()
        self.locale_dir = Path(locale_dir) if locale_dir else None
        self.domain = domain
        self.translation = gettext.translation(domain, self._dir(), fallback=True)
        self.current_language = _language_of(self.translation)

    def _dir(self) -> Optional[str]:
        return str(self.locale_dir) if self.locale_dir else None

    def detect_system_language(self) -> str:
        """Language selected by the environment (LANGUAGE, LC_ALL, LC_MESSAGES, LANG)."""
        return _language_of(gettext.translation(self.domain, self._dir(), fallback=True))

    def set_language(self, language_code: str) -> bool:
        """
        Explicitly select a language (overrides the environment).

        Returns:
            True when a catalog was found, or the language is English.
        """
        translation = gettext.translation(self.domain, self._dir(),
                                          languages=[language_code], fallback=True)
        found = isinstance(translation, gettext.GNUTranslations)
        if found or language_code.split('_')[0] == 'en':
            self.translation = translation
            self.current_language = _language_of(translation) if found else 'en'
            return True
        return False

    def get_translation(self, message: str, **kwargs) -> str:
        """Get translated message with optional str.format() arguments."""
        translated = self.translation.gettext(message)
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass
        return translated

    def get_plural_translation(self, singular: str, plural: str, count: int, **kwargs) -> str:
        """Get translated message with plural support; {count} is always available."""
        translated = self.translation.ngettext(singular, plural, count)
        kwargs['count'] = count
        try:
            translated = translated.format(**kwargs)
        except Exception:
            pass
        return translated

    def get_available_languages(self) -> Dict[str, str]:
        """Languages with an installed catalog, plus English (the source language)."""
        available = {'en': LANGUAGE_NAMES['en']}
        base = Path(self._dir() or os.path.join(sys.base_prefix, 'share', 'locale'))
        for mo_file in sorted(base.glob(f'*/LC_MESSAGES/{self.domain}.mo')):
            code = mo_file.parent.parent.name
            available[code] = LANGUAGE_NAMES.get(code, code)
        return available

    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language or 'en'

    def get_current_language_name(self) -> str:
        """Get current language name."""
        current = self.get_current_language()
        return LANGUAGE_NAMES.get(current, LANGUAGE_NAMES.get(current.split('_')[0], current))

    def _(self, message: str, **kwargs) -> str:
        """Convenience method for translation."""
        return self.get_translation(message, **kwargs)


# Global i18n manager instance
_i18n_manager = None


def get_i18n_manager(locale_dir: str = None, domain: str = DOMAIN) -> I18nManager:
    """Returns the global i18n manager instance."""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager(locale_dir, domain)
    return _i18n_manager


def _(message: str, **kwargs) -> str:
    """Convenience function for translation."""
    return get_i18n_manager().get_translation(message, **kwargs)


def N_(message: str) -> str:
    """Mark a string for extraction; translate it later with _()."""
    return message


def ngettext(singular: str, plural: str, count: int, **kwargs) -> str:
    """Convenience function for plural translation."""
    return get_i18n_manager().get_plural_translation(singular, plural, count, **kwargs)


def set_language(language_code: str) -> bool:
    """Set current language."""
    return get_i18n_manager().set_language(language_code)


def get_current_language() -> str:
    return get_i18n_manager().get_current_language()


def initialize_i18n(locale_dir: str = None, domain: str = DOMAIN) -> str:
    """Initialize the internationalization system."""
    return get_i18n_manager(locale_dir, domain).get_current_language()
