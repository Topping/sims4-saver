"""
Main application controller exposed to QML.
Coordinates the autosave service and settings.
"""

from PySide6.QtCore import QObject, Property, Signal, Slot

from sims_saver.autosave_service import AutosaveService
from sims_saver.settings_manager import SettingsManager


class AppController(QObject):
    """
    Main controller for the Sims 4 Save Helper.
    Exposes application state and actions to QML.
    """

    # Signals
    isRunningChanged = Signal()
    statusTextChanged = Signal()
    processDetectedChanged = Signal()

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self._settings_manager = settings_manager
        self._autosave_service = AutosaveService(self)
        
        # State
        self._is_running = False
        self._status_text = "Ready to start"
        self._process_detected = False

        # Connect autosave service signals
        self._autosave_service.statusChanged.connect(self._on_status_changed)
        self._autosave_service.processDetectedChanged.connect(self._on_process_detected_changed)
        self._autosave_service.keyPressed.connect(self._on_key_pressed)
        self._autosave_service.keyPressFailed.connect(self._on_key_press_failed)

        # Listen for settings changes to update running service
        self._settings_manager.settingsChanged.connect(self._on_settings_changed)

    # --- Properties ---

    @Property(bool, notify=isRunningChanged)
    def isRunning(self) -> bool:
        """Whether the autosave service is currently running."""
        return self._is_running

    @Property(str, notify=statusTextChanged)
    def statusText(self) -> str:
        """Current status message."""
        return self._status_text

    @Property(bool, notify=processDetectedChanged)
    def processDetected(self) -> bool:
        """Whether The Sims 4 process was detected."""
        return self._process_detected

    # --- Slots (actions callable from QML) ---

    @Slot()
    def start(self):
        """Start the autosave service."""
        if self._is_running:
            return

        # Configure service with current settings
        self._autosave_service.configure(
            interval_seconds=self._settings_manager.intervalSeconds,
            key_id=self._settings_manager.selectedKey,
            test_mode=self._settings_manager.testMode
        )

        # Start the background thread
        self._autosave_service.start()
        
        self._is_running = True
        self._status_text = "Starting..."
        self.isRunningChanged.emit()
        self.statusTextChanged.emit()

    @Slot()
    def stop(self):
        """Stop the autosave service."""
        if not self._is_running:
            return

        # Request stop and wait
        self._autosave_service.stop()
        self._autosave_service.wait(2000)  # Wait up to 2 seconds

        self._is_running = False
        self._process_detected = False
        self._status_text = "Ready to start"
        self.isRunningChanged.emit()
        self.processDetectedChanged.emit()
        self.statusTextChanged.emit()

    # --- Internal signal handlers ---

    def _on_status_changed(self, status: str):
        """Handle status updates from autosave service."""
        self._status_text = status
        self.statusTextChanged.emit()

    def _on_process_detected_changed(self, detected: bool):
        """Handle process detection state changes."""
        self._process_detected = detected
        self.processDetectedChanged.emit()

    def _on_key_pressed(self):
        """Handle successful key press."""
        # Could add additional logging or notifications here
        pass

    def _on_key_press_failed(self):
        """Handle failed key press."""
        # Could add error handling or notifications here
        pass

    def _on_settings_changed(self):
        """Handle settings changes while service may be running."""
        if self._is_running:
            # Update service configuration on the fly
            self._autosave_service.configure(
                interval_seconds=self._settings_manager.intervalSeconds,
                key_id=self._settings_manager.selectedKey,
                test_mode=self._settings_manager.testMode
            )

    def cleanup(self):
        """Clean up resources before application exit."""
        if self._is_running:
            self.stop()
