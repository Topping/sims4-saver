"""
Keyboard simulation service for sending save key combinations.
Uses pynput for cross-platform keyboard control.
"""

from pynput.keyboard import Controller, Key


class KeyboardService:
    """Handles keyboard simulation for triggering game saves."""

    def __init__(self):
        self._keyboard = Controller()

    def press_key(self, key_id: str) -> bool:
        """
        Press the specified key or key combination.
        
        Args:
            key_id: The key identifier (e.g., "escape", "f5", "ctrl+s")
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if key_id == "escape":
                self._keyboard.press(Key.esc)
                self._keyboard.release(Key.esc)
            elif key_id == "f5":
                self._keyboard.press(Key.f5)
                self._keyboard.release(Key.f5)
            elif key_id == "f9":
                self._keyboard.press(Key.f9)
                self._keyboard.release(Key.f9)
            elif key_id == "ctrl+s":
                with self._keyboard.pressed(Key.ctrl):
                    self._keyboard.press("s")
                    self._keyboard.release("s")
            elif key_id == "ctrl+shift+s":
                with self._keyboard.pressed(Key.ctrl):
                    with self._keyboard.pressed(Key.shift):
                        self._keyboard.press("s")
                        self._keyboard.release("s")
            else:
                # Default to escape if unknown key
                self._keyboard.press(Key.esc)
                self._keyboard.release(Key.esc)

            return True

        except Exception as e:
            print(f"Error simulating key press: {e}")
            return False
