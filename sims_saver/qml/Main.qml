import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 420
    height: 580
    minimumWidth: 380
    minimumHeight: 500
    title: { Translator.langCode; return Translator.tr("app_title") }

    Material.theme: Material.Light
    Material.accent: Material.Indigo
    Material.primary: Material.Indigo

    // Stack-based navigation
    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: homeView
    }

    Component {
        id: homeView
        HomeView {
            onSettingsRequested: stackView.push(settingsView)
        }
    }

    Component {
        id: settingsView
        SettingsView {
            onBackRequested: stackView.pop()
        }
    }
}
