"""
Autosave service that runs in a background thread.
Periodically checks for The Sims 4 and triggers save key presses.
"""

import time
from typing import Callable, Optional

from PySide6.QtCore import QThread, Signal

from sims_saver.keyboard_service import KeyboardService
from sims_saver.process_detector import ProcessDetector


class AutosaveService(QThread):
    """
    Background service for automatic save reminders.
    
    Signals:
        statusChanged: Emitted when the service status changes
        processDetectedChanged: Emitted when game detection state changes
        processNameChanged: Emitted when the detected process name changes
        keyPressed: Emitted when a key is successfully pressed
        keyPressFailed: Emitted when a key press fails
    """

    # Signals
    statusChanged = Signal(str)
    processDetectedChanged = Signal(bool)
    processNameChanged = Signal(str)
    keyPressed = Signal()
    keyPressFailed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process_detector = ProcessDetector()
        self._keyboard_service = KeyboardService()
        
        # Configuration (updated from main thread)
        self._interval_seconds = 600  # 10 minutes default
        self._key_id = "escape"
        self._test_mode = False
        self._manual_process = ""  # User-selected process override
        
        # State
        self._running = False
        self._process_detected = False
        self._detected_process_name = ""

    def configure(
        self,
        interval_seconds: int,
        key_id: str,
        test_mode: bool
    ):
        """
        Configure the service parameters.
        Call this before starting or to update settings while running.
        
        Args:
            interval_seconds: Time between save triggers
            key_id: Key identifier to press
            test_mode: If True, press keys even without game running
        """
        self._interval_seconds = interval_seconds
        self._key_id = key_id
        self._test_mode = test_mode

    def set_manual_process(self, process_name: str):
        """Set a manual process name to monitor instead of auto-detection."""
        self._manual_process = process_name
        # Emit immediate status update if running with a process selected
        if process_name and self._running:
            self.statusChanged.emit("Running - Waiting for next interval")

    def stop(self):
        """Request the service to stop."""
        self._running = False

    @property
    def is_process_detected(self) -> bool:
        """Check if the game was detected in the last scan."""
        return self._process_detected

    def run(self):
        """Main service loop running in background thread."""
        self._running = True
        
        while self._running:
            try:
                # Check for game process
                if self._manual_process:
                    # Manual process mode - check if specific process is running
                    game_running = self._process_detector.is_process_running(self._manual_process)
                    process_name = self._manual_process if game_running else ""
                else:
                    # Auto-detection mode
                    game_running = self._process_detector.is_sims4_running()
                    process_name = self._process_detector.get_detected_process_name() or ""
                
                # Update process detection state
                if game_running != self._process_detected:
                    self._process_detected = game_running
                    self.processDetectedChanged.emit(game_running)
                
                # Update process name if changed
                if process_name != self._detected_process_name:
                    self._detected_process_name = process_name
                    self.processNameChanged.emit(process_name)

                # Determine if we should press the key
                should_press = self._test_mode or game_running

                if should_press:
                    if self._test_mode:
                        self.statusChanged.emit("Test Mode - Pressing key...")
                    else:
                        self.statusChanged.emit("Game detected - Pressing key...")

                    # Press the configured key
                    if self._keyboard_service.press_key(self._key_id):
                        self.keyPressed.emit()
                        self.statusChanged.emit("Key pressed successfully")
                    else:
                        self.keyPressFailed.emit()
                        self.statusChanged.emit("Key press failed")

                    # Brief pause after key press
                    self._interruptible_sleep(2)

                    if self._running:
                        if self._test_mode:
                            self.statusChanged.emit("Test Mode - Waiting...")
                        else:
                            self.statusChanged.emit("Running - Waiting for next interval")
                else:
                    self.statusChanged.emit("Waiting for The Sims 4...")

                # Wait for next interval
                self._interruptible_sleep(self._interval_seconds)

            except Exception as e:
                print(f"Error in autosave loop: {e}")
                self.statusChanged.emit("Error occurred")
                self._interruptible_sleep(5)

        # Cleanup when stopped
        self._process_detected = False
        self.processDetectedChanged.emit(False)
        self.statusChanged.emit("Stopped")

    def _interruptible_sleep(self, seconds: float):
        """
        Sleep that can be interrupted by stop().
        Checks every 0.5 seconds if we should continue.
        
        Args:
            seconds: Total time to sleep
        """
        elapsed = 0.0
        while elapsed < seconds and self._running:
            sleep_time = min(0.5, seconds - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
