"""
Localization support for The Sims 4 Save Helper.
Provides translations that can be accessed from both Python and QML.
"""

from PySide6.QtCore import QObject, Property, Signal, Slot


class Translator(QObject):
    """
    Translation provider for the application.
    Exposes localized strings as QML properties.
    """

    languageChanged = Signal()

    # English translations
    _EN_TRANSLATIONS = {
        "app_title": "The Sims 4 Save Helper",
        "app_subtitle": "Automatic save reminder system",
        "status_ready": "Ready to start",
        "status_starting": "Starting...",
        "status_stopped": "Stopped",
        "status_test_mode_pressing": "Test Mode - Pressing key...",
        "status_game_detected_pressing": "Game detected - Pressing key...",
        "status_key_pressed": "Key pressed successfully",
        "status_key_failed": "Key press failed",
        "status_test_mode_waiting": "Test Mode - Waiting...",
        "status_running_waiting": "Running - Waiting for next interval",
        "status_waiting_for_game": "Waiting for The Sims 4...",
        "status_error": "Error occurred",
        "settings": "Settings",
        "back": "Back",
        "save_interval": "Save Interval",
        "save_interval_desc": "How often should the helper press the save key?",
        "key_to_press": "Key to Press",
        "key_to_press_desc": "Which key should be pressed to trigger save?",
        "language": "Language",
        "advanced": "Advanced",
        "test_mode": "Test Mode",
        "test_mode_desc": "Press keys even when The Sims 4 is not running",
        "reset_defaults": "Reset to Defaults",
        "start_helper": "Start Helper",
        "stop_helper": "Stop Helper",
        "current_settings": "Current Settings",
        "interval_label": "Interval: {interval}",
        "key_label": "Key: {key}",
        "waiting_for_sims": "Waiting for The Sims 4 to start...",
        "info_text": "This app will press your selected key when The Sims 4 is running to remind you to save.",
        # Additional UI strings
        "select_process": "Select Process",
        "search_processes": "Search processes...",
        "game_detected": "Game detected",
        "no_game_detected": "No game detected",
        "clear_selection": "Clear selection",
        "launch_sims_help": "Launch The Sims 4 and it will be detected automatically",
        "select_process_manually": "Select a process manually",
        # Interval options
        "interval_1_min": "1 minute",
        "interval_2_min": "2 minutes",
        "interval_5_min": "5 minutes",
        "interval_10_min": "10 minutes",
        "interval_15_min": "15 minutes",
        "interval_30_min": "30 minutes",
        # Key descriptions
        "key_desc_escape": "Opens the game menu for manual saving",
        "key_desc_f5": "Common quicksave key in many games",
        "key_desc_f9": "Alternative quicksave key",
        "key_desc_ctrl_s": "Standard save shortcut",
        "key_desc_ctrl_shift_s": "Custom save combination",
    }

    # Danish translations
    _DA_TRANSLATIONS = {
        "app_title": "The Sims 4 Save Helper",
        "app_subtitle": "Automatisk gemmepåmindelsessystem",
        "status_ready": "Klar til at starte",
        "status_starting": "Starter...",
        "status_stopped": "Stoppet",
        "status_test_mode_pressing": "Testtilstand - Trykker på tast...",
        "status_game_detected_pressing": "Spil fundet - Trykker på tast...",
        "status_key_pressed": "Tast trykket korrekt",
        "status_key_failed": "Tastetryk mislykkedes",
        "status_test_mode_waiting": "Testtilstand - Venter...",
        "status_running_waiting": "Kører - Venter på næste interval",
        "status_waiting_for_game": "Venter på The Sims 4...",
        "status_error": "Fejl opstod",
        "settings": "Indstillinger",
        "back": "Tilbage",
        "save_interval": "Interval",
        "save_interval_desc": "Hvor ofte skal hjælperen trykke på gemmetasten?",
        "key_to_press": "Tast til at trykke på",
        "key_to_press_desc": "Hvilken tast skal trykkes for at gemme?",
        "language": "Sprog",
        "advanced": "Avanceret",
        "test_mode": "Testtilstand",
        "test_mode_desc": "Tryk på taster selvom The Sims 4 ikke kører",
        "reset_defaults": "Nulstil Indstillinger",
        "start_helper": "Start hjælper",
        "stop_helper": "Stop hjælper",
        "current_settings": "Aktuelle indstillinger",
        "interval_label": "Interval: {interval}",
        "key_label": "Tast: {key}",
        "waiting_for_sims": "Venter på at The Sims 4 starter...",
        "info_text": "Denne app trykker på din valgte tast, når The Sims 4 kører, for at minde dig om at gemme.",
        # Additional UI strings
        "select_process": "Vælg proces",
        "search_processes": "Søg processer...",
        "game_detected": "Spil fundet",
        "no_game_detected": "Intet spil fundet",
        "clear_selection": "Ryd valg",
        "launch_sims_help": "Start The Sims 4 og det vil blive registreret automatisk",
        "select_process_manually": "Vælg en proces manuelt",
        # Interval options
        "interval_1_min": "1 minut",
        "interval_2_min": "2 minutter",
        "interval_5_min": "5 minutter",
        "interval_10_min": "10 minutter",
        "interval_15_min": "15 minutter",
        "interval_30_min": "30 minutter",
        # Key descriptions
        "key_desc_escape": "Åbner spilmenuen for manuel gemning",
        "key_desc_f5": "Almindelig quicksave-tast i mange spil",
        "key_desc_f9": "Alternativ quicksave-tast",
        "key_desc_ctrl_s": "Standard genvej til gemning",
        "key_desc_ctrl_shift_s": "Tilpasset genvejskombination",
    }

    _ALL_TRANSLATIONS = {
        "en": _EN_TRANSLATIONS,
        "da": _DA_TRANSLATIONS,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lang_code = "en"
        self._translations = self._EN_TRANSLATIONS

    def set_language(self, lang_code: str):
        """Set the current language."""
        if lang_code in self._ALL_TRANSLATIONS:
            self._lang_code = lang_code
            self._translations = self._ALL_TRANSLATIONS[lang_code]
            self.languageChanged.emit()

    # Property for QML to bind to - triggers re-evaluation of translations
    @Property(str, notify=languageChanged)
    def langCode(self) -> str:
        """Current language code - bind to this in QML to trigger updates."""
        return self._lang_code

    @Slot(str, result=str)
    def tr(self, key: str) -> str:
        """Get a translated string by key."""
        return self._translations.get(key, key)

    @Slot(str, str, result=str)
    def trFormat(self, key: str, arg: str) -> str:
        """Get a translated string with format substitution."""
        template = self._translations.get(key, key)
        # Simple placeholder replacement
        return template.replace("{interval}", arg).replace("{key}", arg)

    # Expose common strings as properties for QML binding
    @Property(str, notify=languageChanged)
    def appTitle(self):
        return self.tr("app_title")

    @Property(str, notify=languageChanged)
    def settings(self):
        return self.tr("settings")

    @Property(str, notify=languageChanged)
    def back(self):
        return self.tr("back")

    @Property(str, notify=languageChanged)
    def startHelper(self):
        return self.tr("start_helper")

    @Property(str, notify=languageChanged)
    def stopHelper(self):
        return self.tr("stop_helper")


# For backward compatibility and standalone usage
class Localization:
    """Legacy localization class for backward compatibility."""

    def __init__(self, lang_code: str = "en"):
        self.lang_code = lang_code
        self.translations = Translator._ALL_TRANSLATIONS.get(
            lang_code, Translator._EN_TRANSLATIONS
        )

    def get(self, key: str, **kwargs) -> str:
        """Get a translated string with optional format arguments."""
        template = self.translations.get(key, key)
        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError:
                return template
        return template
