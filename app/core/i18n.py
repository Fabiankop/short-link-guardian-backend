from babel.support import Translations
import os

def get_translations(locale: str = "en") -> Translations:
    translations_dir = os.path.join(os.path.dirname(__file__), "..", "locales")
    return Translations.load(translations_dir, [locale])
