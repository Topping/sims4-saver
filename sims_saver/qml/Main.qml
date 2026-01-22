import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 420
    height: 580
    minimumWidth: 380
    minimumHeight: 500
    title: qsTr("The Sims 4 Save Helper")
    
    // Color palette
    readonly property color primaryColor: "#6366F1"
    readonly property color primaryDarkColor: "#4F46E5"
    readonly property color backgroundColor: "#F8FAFC"
    readonly property color cardColor: "#FFFFFF"
    readonly property color textColor: "#1E293B"
    readonly property color textSecondaryColor: "#64748B"
    readonly property color successColor: "#10B981"
    readonly property color warningColor: "#F59E0B"
    readonly property color errorColor: "#EF4444"
    
    color: backgroundColor

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
