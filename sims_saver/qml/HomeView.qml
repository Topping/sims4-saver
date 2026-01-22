import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Page {
    id: root
    
    signal settingsRequested()

    header: ToolBar {
        Material.foreground: "white"
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 8
            
            Label {
                text: { Translator.langCode; return Translator.tr("app_title") }
                font.pixelSize: 18
                font.weight: Font.Medium
                Layout.fillWidth: true
            }
            
            // Language flag dropdown
            ToolButton {
                id: languageButton
                text: SettingsManager.languageIndex === 0 ? "\uD83C\uDDEC\uD83C\uDDE7" : "\uD83C\uDDE9\uD83C\uDDF0"
                font.pixelSize: 24
                implicitWidth: 48
                implicitHeight: 48
                onClicked: languageMenu.open()
                
                background: Rectangle {
                    radius: 24
                    color: languageButton.hovered ? Qt.rgba(255, 255, 255, 0.15) : "transparent"
                }
                
                Menu {
                    id: languageMenu
                    y: languageButton.height
                    
                    MenuItem {
                        text: "\uD83C\uDDEC\uD83C\uDDE7 English"
                        font.pixelSize: 16
                        onTriggered: SettingsManager.languageIndex = 0
                    }
                    MenuItem {
                        text: "\uD83C\uDDE9\uD83C\uDDF0 Dansk"
                        font.pixelSize: 16
                        onTriggered: SettingsManager.languageIndex = 1
                    }
                }
                
                ToolTip.visible: hovered
                ToolTip.text: { Translator.langCode; return Translator.tr("language") }
            }
            
            ToolButton {
                id: settingsButton
                text: "\u2699\uFE0F"
                font.pixelSize: 26
                implicitWidth: 48
                implicitHeight: 48
                onClicked: root.settingsRequested()
                
                background: Rectangle {
                    radius: 24
                    color: settingsButton.hovered ? Qt.rgba(255, 255, 255, 0.15) : "transparent"
                }
                
                ToolTip.visible: hovered
                ToolTip.text: { Translator.langCode; return Translator.tr("settings") }
            }
        }
    }

    // Process selection dialog
    Dialog {
        id: processDialog
        title: { Translator.langCode; return Translator.tr("select_process") }
        modal: true
        anchors.centerIn: parent
        width: Math.min(parent.width - 48, 400)
        height: Math.min(parent.height - 96, 500)
        
        property var filteredProcesses: []
        
        function refreshAndShow() {
            AppController.refreshProcessList()
            searchField.text = ""
            filterProcesses("")
            open()
        }
        
        function filterProcesses(filter) {
            var all = AppController.runningProcesses
            if (filter.length === 0) {
                filteredProcesses = all
            } else {
                var lowerFilter = filter.toLowerCase()
                filteredProcesses = all.filter(function(p) {
                    return p.toLowerCase().indexOf(lowerFilter) !== -1
                })
            }
        }
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 16
            
            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: { Translator.langCode; return Translator.tr("search_processes") }
                onTextChanged: processDialog.filterProcesses(text)
            }
            
            ListView {
                id: processList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: processDialog.filteredProcesses
                
                delegate: ItemDelegate {
                    width: processList.width
                    text: modelData
                    onClicked: {
                        AppController.selectManualProcess(modelData)
                        processDialog.close()
                    }
                }
                
                ScrollIndicator.vertical: ScrollIndicator {}
            }
        }
        
        standardButtons: Dialog.Cancel
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 24

        // Process Status Card
        Pane {
            Layout.fillWidth: true
            Material.elevation: 2
            padding: 20

            ColumnLayout {
                anchors.fill: parent
                spacing: 12

                // Status header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    
                    // Status indicator dot
                    Rectangle {
                        width: 12
                        height: 12
                        radius: 6
                        color: {
                            switch (AppController.detectionState) {
                                case "idle": return Material.color(Material.Grey)
                                case "waiting": return Material.color(Material.Amber)
                                case "no_process": return Material.color(Material.Red)
                                case "running": return Material.color(Material.Green)
                                default: return Material.color(Material.Grey)
                            }
                        }
                    }
                    
                    Label {
                        text: {
                            Translator.langCode  // Trigger re-evaluation on language change
                            switch (AppController.detectionState) {
                                case "idle": return Translator.tr("no_game_detected")
                                case "waiting": return Translator.tr("waiting_to_start")
                                case "no_process": return Translator.tr("no_process_found")
                                case "running": return Translator.tr("running")
                                default: return Translator.tr("no_game_detected")
                            }
                        }
                        font.pixelSize: 16
                        font.weight: Font.Medium
                        Layout.fillWidth: true
                    }
                }
                
                // Show detected/selected process name
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    visible: AppController.detectedProcessName !== ""
                    
                    Label {
                        text: AppController.detectedProcessName
                        font.pixelSize: 14
                        opacity: 0.8
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                    
                    Button {
                        text: "\u00D7"
                        flat: true
                        font.pixelSize: 16
                        implicitWidth: 32
                        implicitHeight: 32
                        visible: AppController.detectedProcessName !== ""
                        onClicked: AppController.clearManualProcess()
                        
                        ToolTip.visible: hovered
                        ToolTip.text: { Translator.langCode; return Translator.tr("clear_selection") }
                    }
                }
                
                // No game detected - show help text
                Label {
                    visible: !AppController.processDetected
                    text: { Translator.langCode; return Translator.tr("launch_sims_help") }
                    font.pixelSize: 13
                    opacity: 0.6
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                // Manual selection button
                Button {
                    visible: !AppController.processDetected
                    text: { Translator.langCode; return Translator.tr("select_process_manually") }
                    flat: true
                    Material.foreground: Material.accent
                    onClicked: processDialog.refreshAndShow()
                }
                
                // Running status
                Rectangle {
                    visible: AppController.isRunning
                    Layout.fillWidth: true
                    height: 1
                    color: Material.dividerColor
                    opacity: 0.5
                    Layout.topMargin: 4
                }
                
                RowLayout {
                    visible: AppController.isRunning
                    Layout.fillWidth: true
                    spacing: 8
                    
                    // Activity indicator
                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: Material.color(Material.Indigo)
                        
                        SequentialAnimation on opacity {
                            running: AppController.isRunning
                            loops: Animation.Infinite
                            NumberAnimation { to: 0.3; duration: 600; easing.type: Easing.InOutQuad }
                            NumberAnimation { to: 1.0; duration: 600; easing.type: Easing.InOutQuad }
                        }
                    }
                    
                    Label {
                        text: AppController.statusText
                        font.pixelSize: 13
                        opacity: 0.7
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        // Current settings summary
        Pane {
            Layout.fillWidth: true
            Material.elevation: 1
            padding: 16

            ColumnLayout {
                anchors.fill: parent
                spacing: 8

                Label {
                    text: { Translator.langCode; return Translator.tr("current_settings") }
                    font.pixelSize: 12
                    font.weight: Font.Medium
                    opacity: 0.6
                }

                Label {
                    text: { Translator.langCode; return Translator.trFormat("interval_label", SettingsManager.intervalDisplayText) }
                    font.pixelSize: 14
                }

                Label {
                    text: { Translator.langCode; return Translator.trFormat("key_label", SettingsManager.keyDisplayText) }
                    font.pixelSize: 14
                }
            }
        }

        Item { Layout.fillHeight: true }

        // Action button
        Button {
            id: actionButton
            Layout.fillWidth: true
            Layout.preferredHeight: 56
            text: { Translator.langCode; return AppController.isRunning ? Translator.tr("stop_helper") : Translator.tr("start_helper") }
            Material.background: AppController.isRunning ? Material.Red : Material.Indigo
            Material.foreground: "white"
            font.pixelSize: 16
            font.weight: Font.Medium
            
            onClicked: {
                if (AppController.isRunning) {
                    AppController.stop()
                } else {
                    AppController.start()
                }
            }
        }

        // Info text
        Label {
            Layout.fillWidth: true
            text: { Translator.langCode; return Translator.tr("info_text") }
            font.pixelSize: 12
            opacity: 0.6
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
