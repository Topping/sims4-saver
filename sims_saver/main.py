#!/usr/bin/env python3
"""
The Sims 4 Save Helper - Main Entry Point

A modern Qt Quick application that automatically presses save keys
at configurable intervals when The Sims 4 is running.
"""

import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from sims_saver.app_controller import AppController
from sims_saver.localization import Translator
from sims_saver.settings_manager import SettingsManager


def get_qml_path() -> Path:
    """Get the path to QML files, handling both development and packaged modes."""
    # When running from source
    source_path = Path(__file__).parent / "qml" / "Main.qml"
    if source_path.exists():
        return source_path

    # When packaged with PyInstaller
    if hasattr(sys, "_MEIPASS"):
        packaged_path = Path(sys._MEIPASS) / "sims_saver" / "qml" / "Main.qml"
        if packaged_path.exists():
            return packaged_path

    raise FileNotFoundError("Could not find QML files")


def get_icon_path() -> Path:
    """Get the path to the application icon."""
    # Try source location first
    base_path = Path(__file__).parent.parent
    icon_path = base_path / "icon.png"
    if icon_path.exists():
        return icon_path

    # Try packaged location
    if hasattr(sys, "_MEIPASS"):
        packaged_path = Path(sys._MEIPASS) / "icon.png"
        if packaged_path.exists():
            return packaged_path

    return None


def main():
    """Main entry point for the application."""
    # Set application metadata (for QSettings)
    QCoreApplication.setOrganizationName("Topping")
    QCoreApplication.setOrganizationDomain("github.com/Topping")
    QCoreApplication.setApplicationName("Sims4SaveHelper")
    
    # Set Qt Quick Controls style to Material for modern appearance
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

    # Create the application
    app = QGuiApplication(sys.argv)
    app.setApplicationDisplayName("The Sims 4 Save Helper")

    # Set application icon
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create the QML engine
    engine = QQmlApplicationEngine()

    # Create singleton instances
    settings_manager = SettingsManager()
    translator = Translator()
    app_controller = AppController(settings_manager)

    # Connect translator to settings manager for translated options
    settings_manager.set_translator(translator)

    # Sync translator language on startup and when settings change
    translator.set_language(settings_manager.languageCode)
    settings_manager.languageIndexChanged.connect(
        lambda: translator.set_language(settings_manager.languageCode)
    )

    # Set context properties for QML access
    engine.rootContext().setContextProperty("AppController", app_controller)
    engine.rootContext().setContextProperty("SettingsManager", settings_manager)
    engine.rootContext().setContextProperty("Translator", translator)

    # Load the main QML file
    qml_path = get_qml_path()
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML")
        sys.exit(-1)

    # Handle application quit
    app.aboutToQuit.connect(app_controller.cleanup)

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
