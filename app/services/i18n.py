"""
Internationalization (i18n) Service for ParkMyCar
Handles translation loading and text rendering
"""

import json
from pathlib import Path
from typing import Dict, Optional
import logging


class I18nService:
    """Service for managing translations"""
    
    _translations: Dict[str, Dict] = {}
    DEFAULT_LOCALE = "en"
    SUPPORTED_LOCALES = ["en", "ms"]
    
    @classmethod
    def load_translations(cls):
        """Load all translation files at startup"""
        if cls._translations:
            return  # Already loaded
        
        try:
            base_path = Path(__file__).resolve().parents[2] / "i18n"
            
            for locale in cls.SUPPORTED_LOCALES:
                file_path = base_path / f"{locale}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cls._translations[locale] = json.load(f)
                    logging.info(f"✅ Loaded {locale} translations")
                else:
                    logging.warning(f"⚠️ Translation file not found: {file_path}")
            
            logging.info(f"🌍 i18n initialized with {len(cls._translations)} languages")
        except Exception as e:
            logging.exception(f"❌ Error loading translations: {e}")
            cls._translations = {cls.DEFAULT_LOCALE: {}}
    
    @classmethod
    def t(cls, key: str, locale: str = None, **params) -> str:
        """
        Translate a key with optional parameters
        
        Args:
            key: Translation key (e.g., "nav.home")
            locale: Language code ("en" or "ms")
            **params: Parameters for string formatting
        
        Returns:
            Translated string
        
        Example:
            t("nav.home", "en")  # "Home"
            t("nav.home", "ms")  # "Laman Utama"
            t("listings.spots_available", "en", count=5)  # "5 spots available"
        """
        # Ensure translations are loaded
        if not cls._translations:
            cls.load_translations()
        
        # Use default if locale not provided
        loc = locale or cls.DEFAULT_LOCALE
        
        # Get catalog for locale (fallback to English)
        catalog = cls._translations.get(loc, cls._translations.get(cls.DEFAULT_LOCALE, {}))
        
        # Navigate nested keys (e.g., "nav.home" -> catalog["nav"]["home"])
        parts = key.split('.')
        value = catalog
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        
        # If not found, try English fallback
        if value is None and loc != cls.DEFAULT_LOCALE:
            value = cls._get_fallback(key)
        
        # If still not found, return the key itself
        if value is None:
            logging.warning(f"⚠️ Translation key not found: {key}")
            return key
        
        # Format with parameters if provided
        if isinstance(value, str) and params:
            try:
                return value.format(**params)
            except (KeyError, ValueError) as e:
                logging.warning(f"⚠️ Error formatting translation '{key}': {e}")
                return value
        
        return str(value) if value is not None else key
    
    @classmethod
    def _get_fallback(cls, key: str) -> Optional[str]:
        """Get English fallback for missing key"""
        parts = key.split('.')
        value = cls._translations.get(cls.DEFAULT_LOCALE, {})
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        
        return value


# Initialize translations at module load
I18nService.load_translations()


# Convenience function for easy import
def t(key: str, locale: str = None, **params) -> str:
    """
    Translate a key (shorthand for I18nService.t)
    
    Usage:
        from app.services.i18n import t
        
        title = t("nav.home", locale)
        message = t("listings.spots_available", locale, count=10)
    """
    return I18nService.t(key, locale, **params)


def get_supported_locales():
    """Get list of supported language codes"""
    return I18nService.SUPPORTED_LOCALES


def get_locale_name(locale: str) -> str:
    """Get display name for a locale"""
    names = {
        "en": "English",
        "ms": "Bahasa Melayu"
    }
    return names.get(locale, locale)
