"""
Main application controller exposed to QML.
Coordinates the autosave service and settings.
"""

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer

from sims_saver.autosave_service import AutosaveService
from sims_saver.process_detector import ProcessDetector
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
    detectedProcessNameChanged = Signal()
    runningProcessesChanged = Signal()

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self._settings_manager = settings_manager
        self._autosave_service = AutosaveService(self)
        self._process_detector = ProcessDetector()
        
        # State
        self._is_running = False
        self._status_text = ""
        self._process_detected = False
        self._detected_process_name = ""
        self._manual_process_name = ""  # User-selected process override

        # Background process detection timer (runs even when helper is stopped)
        self._detection_timer = QTimer(self)
        self._detection_timer.timeout.connect(self._check_for_process)
        self._detection_timer.start(2000)  # Check every 2 seconds

        # Connect autosave service signals
        self._autosave_service.statusChanged.connect(self._on_status_changed)
        self._autosave_service.processDetectedChanged.connect(self._on_process_detected_changed)
        self._autosave_service.processNameChanged.connect(self._on_process_name_changed)
        self._autosave_service.keyPressed.connect(self._on_key_pressed)
        self._autosave_service.keyPressFailed.connect(self._on_key_press_failed)

        # Listen for settings changes to update running service
        self._settings_manager.settingsChanged.connect(self._on_settings_changed)
        
        # Do initial process check
        self._check_for_process()

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

    @Property(str, notify=detectedProcessNameChanged)
    def detectedProcessName(self) -> str:
        """Name of the detected process."""
        return self._detected_process_name

    @Property(list, notify=runningProcessesChanged)
    def runningProcesses(self) -> list:
        """List of currently running process names."""
        return self._process_detector.get_all_running_processes()

    # --- Slots (actions callable from QML) ---

    @Slot()
    def refreshProcessList(self):
        """Refresh the list of running processes."""
        self.runningProcessesChanged.emit()

    def _check_for_process(self):
        """Periodically check for the game process (runs even when helper is stopped)."""
        # Skip if helper is running (autosave service handles detection)
        if self._is_running:
            return
            
        # Skip if user manually selected a process
        if self._manual_process_name:
            return
        
        # Auto-detect Sims 4
        was_detected = self._process_detected
        old_name = self._detected_process_name
        
        if self._process_detector.is_sims4_running():
            self._process_detected = True
            self._detected_process_name = self._process_detector.get_detected_process_name() or "The Sims 4"
        else:
            self._process_detected = False
            self._detected_process_name = ""
        
        # Emit signals if changed
        if was_detected != self._process_detected:
            self.processDetectedChanged.emit()
        if old_name != self._detected_process_name:
            self.detectedProcessNameChanged.emit()

    @Slot(str)
    def selectManualProcess(self, process_name: str):
        """Manually select a process to monitor."""
        self._manual_process_name = process_name
        self._detected_process_name = process_name
        self._process_detected = True
        self.detectedProcessNameChanged.emit()
        self.processDetectedChanged.emit()
        
        # Update the autosave service with manual process
        if self._is_running:
            self._autosave_service.set_manual_process(process_name)

    @Slot()
    def clearManualProcess(self):
        """Clear manual process selection, return to auto-detection."""
        self._manual_process_name = ""
        self._detected_process_name = ""
        self._process_detected = False
        self.detectedProcessNameChanged.emit()
        self.processDetectedChanged.emit()
        
        if self._is_running:
            self._autosave_service.set_manual_process("")

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
        
        # Set manual process if one was selected
        if self._manual_process_name:
            self._autosave_service.set_manual_process(self._manual_process_name)

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

    def _on_process_name_changed(self, name: str):
        """Handle detected process name changes."""
        if not self._manual_process_name:  # Only update if not manually set
            self._detected_process_name = name
            self.detectedProcessNameChanged.emit()

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
