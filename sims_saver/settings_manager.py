"""
Settings manager for Sims 4 Save Helper.
Uses QSettings for platform-appropriate persistent storage.
"""

from PySide6.QtCore import QObject, Property, Signal, QSettings, Slot


class SettingsManager(QObject):
    """Manages application settings with QML-bindable properties."""

    # Signals for property change notifications
    intervalIndexChanged = Signal()
    keyIndexChanged = Signal()
    languageIndexChanged = Signal()
    testModeChanged = Signal()
    settingsChanged = Signal()

    # Fixed interval options (in seconds) - simplified from slider
    INTERVAL_OPTIONS = [
        (60, "1 minute"),
        (120, "2 minutes"),
        (300, "5 minutes"),
        (600, "10 minutes"),
        (900, "15 minutes"),
        (1800, "30 minutes"),
    ]

    # Key options with descriptions
    KEY_OPTIONS = [
        ("escape", "Escape", "Opens the game menu for manual saving"),
        ("f5", "F5", "Common quicksave key in many games"),
        ("f9", "F9", "Alternative quicksave key"),
        ("ctrl+s", "Ctrl+S", "Standard save shortcut"),
        ("ctrl+shift+s", "Ctrl+Shift+S", "Custom save combination"),
    ]

    # Language options
    LANGUAGE_OPTIONS = [
        ("en", "English"),
        ("da", "Danish"),
    ]

    # Default settings
    DEFAULTS = {
        "interval_index": 2,  # 5 minutes
        "key_index": 0,  # Escape
        "language_index": 0,  # English
        "test_mode": False,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("Topping", "Sims4SaveHelper")
        self._load_settings()

    def _load_settings(self):
        """Load settings from persistent storage."""
        self._interval_index = int(
            self._settings.value("interval_index", self.DEFAULTS["interval_index"])
        )
        self._key_index = int(
            self._settings.value("key_index", self.DEFAULTS["key_index"])
        )
        self._language_index = int(
            self._settings.value("language_index", self.DEFAULTS["language_index"])
        )
        self._test_mode = self._settings.value("test_mode", self.DEFAULTS["test_mode"])
        # Handle QSettings returning string "true"/"false" on some platforms
        if isinstance(self._test_mode, str):
            self._test_mode = self._test_mode.lower() == "true"

    def _save_settings(self):
        """Save current settings to persistent storage."""
        self._settings.setValue("interval_index", self._interval_index)
        self._settings.setValue("key_index", self._key_index)
        self._settings.setValue("language_index", self._language_index)
        self._settings.setValue("test_mode", self._test_mode)
        self._settings.sync()
        self.settingsChanged.emit()

    # --- Interval property ---

    @Property(int, notify=intervalIndexChanged)
    def intervalIndex(self):
        return self._interval_index

    @intervalIndex.setter
    def intervalIndex(self, value):
        if 0 <= value < len(self.INTERVAL_OPTIONS) and value != self._interval_index:
            self._interval_index = value
            self._save_settings()
            self.intervalIndexChanged.emit()

    @Property(list, constant=True)
    def intervalOptions(self):
        return [opt[1] for opt in self.INTERVAL_OPTIONS]

    @Property(str, notify=intervalIndexChanged)
    def intervalDisplayText(self):
        return self.INTERVAL_OPTIONS[self._interval_index][1]

    @Property(int, notify=intervalIndexChanged)
    def intervalSeconds(self):
        """Get the current interval in seconds."""
        return self.INTERVAL_OPTIONS[self._interval_index][0]

    # --- Key property ---

    @Property(int, notify=keyIndexChanged)
    def keyIndex(self):
        return self._key_index

    @keyIndex.setter
    def keyIndex(self, value):
        if 0 <= value < len(self.KEY_OPTIONS) and value != self._key_index:
            self._key_index = value
            self._save_settings()
            self.keyIndexChanged.emit()

    @Property(list, constant=True)
    def keyOptions(self):
        return [opt[1] for opt in self.KEY_OPTIONS]

    @Property(str, notify=keyIndexChanged)
    def keyDisplayText(self):
        return self.KEY_OPTIONS[self._key_index][1]

    @Property(str, notify=keyIndexChanged)
    def keyDescription(self):
        return self.KEY_OPTIONS[self._key_index][2]

    @Property(str, notify=keyIndexChanged)
    def selectedKey(self):
        """Get the internal key identifier."""
        return self.KEY_OPTIONS[self._key_index][0]

    # --- Language property ---

    @Property(int, notify=languageIndexChanged)
    def languageIndex(self):
        return self._language_index

    @languageIndex.setter
    def languageIndex(self, value):
        if 0 <= value < len(self.LANGUAGE_OPTIONS) and value != self._language_index:
            self._language_index = value
            self._save_settings()
            self.languageIndexChanged.emit()

    @Property(list, constant=True)
    def languageOptions(self):
        return [opt[1] for opt in self.LANGUAGE_OPTIONS]

    @Property(str, notify=languageIndexChanged)
    def languageCode(self):
        """Get the current language code."""
        return self.LANGUAGE_OPTIONS[self._language_index][0]

    # --- Test mode property ---

    @Property(bool, notify=testModeChanged)
    def testMode(self):
        return self._test_mode

    @testMode.setter
    def testMode(self, value):
        if value != self._test_mode:
            self._test_mode = value
            self._save_settings()
            self.testModeChanged.emit()

    # --- Actions ---

    @Slot()
    def resetToDefaults(self):
        """Reset all settings to default values."""
        self._interval_index = self.DEFAULTS["interval_index"]
        self._key_index = self.DEFAULTS["key_index"]
        self._language_index = self.DEFAULTS["language_index"]
        self._test_mode = self.DEFAULTS["test_mode"]
        self._save_settings()
        self.intervalIndexChanged.emit()
        self.keyIndexChanged.emit()
        self.languageIndexChanged.emit()
        self.testModeChanged.emit()
