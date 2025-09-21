# sims_saver/localization.py

import json
import os

class Localization:
    def __init__(self, lang_code="English"):
        self.lang_code = lang_code
        self.translations = self._load_translations()

    def _load_translations(self):
        # Default English translations
        en_translations = {
            "app_title": "The Sims 4 Save Helper",
            "app_subtitle": "Automatic save reminder system",
            "save_interval_title": "Save Interval",
            "seconds_singular": "second",
            "seconds_plural": "seconds",
            "minutes_singular": "minute",
            "minutes_plural": "minutes",
            "one_sec": "1 sec",
            "thirty_min": "30 min",
            "key_to_press_title": "Key to Press",
            "key_escape": "Escape (opens menu)",
            "key_f5": "F5 (common save key)",
            "key_f9": "F9 (common quicksave key)",
            "key_ctrl_s": "Ctrl+S (standard save)",
            "key_ctrl_shift_s": "Ctrl+Shift+S (custom save)",
            "test_mode_checkbox": "Test Mode - Press keys regardless of game status",
            "monitored_process_title": "Monitored Process",
            "currently_monitoring": "Currently monitoring: {process_names}",
            "select_custom_process_button": "Select Custom Process",
            "status_title": "Status",
            "status_ready": "Ready to start",
            "status_test_mode_pressing": "Test Mode - Pressing key...",
            "status_game_detected_pressing": "Game detected - Pressing key...",
            "status_key_pressed_success": "✅ Key pressed successfully",
            "status_key_press_failed": "❌ Key press failed",
            "status_test_mode_waiting": "Test Mode - Waiting for next interval",
            "status_running_waiting": "Running - Waiting for next interval",
            "status_waiting_for_process": "🔍 Waiting for monitored process...",
            "status_error_occurred": "⚠️ Error occurred",
            "start_helper_button": "Start Helper",
            "stop_helper_button": "Stop Helper",
            "revert_to_defaults_button": "Revert to Defaults",
            "info_text": "💡 This app will press your selected key when The Sims 4 is running.\nUse Test Mode to verify functionality. Ensure the game has focus when keys are pressed.",
            "select_process_dialog_title": "Select Process to Monitor",
            "select_process_dialog_header": "Select a process from the list:",
            "select_button": "Select",
            "cancel_button": "Cancel",
            "settings_reverted": "Settings reverted to defaults",
            "play_sound_cue_title": "Sound Cue",
            "play_sound_cue_checkbox": "Play a sound cue when key is pressed"
        }

        # Danish translations
        da_translations = {
            "app_title": "The Sims 4 Save Helper",
            "app_subtitle": "Automatisk gemmepåmindelsessystem",
            "save_interval_title": "Interval",
            "seconds_singular": "sekund",
            "seconds_plural": "sekunder",
            "minutes_singular": "minut",
            "minutes_plural": "minutter",
            "one_sec": "1 sek",
            "thirty_min": "30 min",
            "key_to_press_title": "Tast til at trykke på",
            "key_escape": "Escape (åbner menu)",
            "key_f5": "F5 (almindelig gemmetast)",
            "key_f9": "F9 (almindelig hurtiggemmetast)",
            "key_ctrl_s": "Ctrl+S (standard gem)",
            "key_ctrl_shift_s": "Ctrl+Shift+S (brugerdefineret gem)",
            "test_mode_checkbox": "Testtilstand - Tryk på taster uanset spilstatus",
            "monitored_process_title": "Overvåget proces",
            "currently_monitoring": "Overvåger i øjeblikket: {process_names}",
            "select_custom_process_button": "Vælg brugerdefineret proces",
            "status_title": "Status",
            "status_ready": "Klar til at starte",
            "status_test_mode_pressing": "Testtilstand - Trykker på tast...",
            "status_game_detected_pressing": "Spil fundet - Trykker på tast...",
            "status_key_pressed_success": "✅ Tast trykket korrekt",
            "status_key_press_failed": "❌ Tastetryk mislykkedes",
            "status_test_mode_waiting": "Testtilstand - Venter på næste interval",
            "status_running_waiting": "Kører - Venter på næste interval",
            "status_waiting_for_process": "🔍 Venter på overvåget proces...",
            "status_error_occurred": "⚠️ Fejl opstod",
            "start_helper_button": "Start hjælper",
            "stop_helper_button": "Stop hjælper",
            "revert_to_defaults_button": "Nulstil Indstillinger",
            "info_text": "💡 Denne app trykker på din valgte tast, når The Sims 4 kører.\nBrug Testtilstand til at verificere funktionalitet. Sørg for, at spillet er i fokus, når der trykkes på taster.",
            "select_process_dialog_title": "Vælg proces til overvågning",
            "select_process_dialog_header": "Vælg en proces fra listen:",
            "select_button": "Vælg",
            "cancel_button": "Annuller",
            "settings_reverted": "Indstillinger nulstillet til standard",
            "play_sound_cue_title": "Lydsignal",
            "play_sound_cue_checkbox": "Afspil lydsignal når tasten trykkes"
        }

        all_translations = {
            "en": en_translations,
            "da": da_translations
        }
        
        return all_translations.get(self.lang_code, en_translations)

    def get(self, key, **kwargs):
        return self.translations.get(key, key).format(**kwargs)

# Example usage (for testing purposes)
if __name__ == "__main__":
    loc_en = Localization("en")
    print(f"English App Title: {loc_en.get('app_title')}")
    print(f"English Monitoring: {loc_en.get('currently_monitoring', process_names='ts4.exe, ts4_x64.exe')}")

    loc_da = Localization("da")
    print(f"Danish App Title: {loc_da.get('app_title')}")
    print(f"Danish Monitoring: {loc_da.get('currently_monitoring', process_names='ts4.exe, ts4_x64.exe')}")
