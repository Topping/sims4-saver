import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Page {
    id: root
    
    signal backRequested()

    header: ToolBar {
        Material.foreground: "white"
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 4
            anchors.rightMargin: 16
            
            ToolButton {
                text: "\u2190"
                font.pixelSize: 20
                onClicked: root.backRequested()
            }
            
            Label {
                text: { Translator.langCode; return Translator.tr("settings") }
                font.pixelSize: 18
                font.weight: Font.Medium
                Layout.fillWidth: true
            }
        }
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth

        ColumnLayout {
            width: parent.width
            spacing: 0

            // Interval Section
            Pane {
                Layout.fillWidth: true
                padding: 20

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12

                    Label {
                        text: { Translator.langCode; return Translator.tr("save_interval") }
                        font.pixelSize: 14
                        font.weight: Font.Medium
                    }

                    Label {
                        text: { Translator.langCode; return Translator.tr("save_interval_desc") }
                        font.pixelSize: 12
                        opacity: 0.6
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    ComboBox {
                        id: intervalCombo
                        Layout.fillWidth: true
                        model: SettingsManager.intervalOptions
                        currentIndex: SettingsManager.intervalIndex
                        onCurrentIndexChanged: SettingsManager.intervalIndex = currentIndex
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Material.dividerColor
            }

            // Key Section
            Pane {
                Layout.fillWidth: true
                padding: 20

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12

                    Label {
                        text: { Translator.langCode; return Translator.tr("key_to_press") }
                        font.pixelSize: 14
                        font.weight: Font.Medium
                    }

                    Label {
                        text: { Translator.langCode; return Translator.tr("key_to_press_desc") }
                        font.pixelSize: 12
                        opacity: 0.6
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    ComboBox {
                        id: keyCombo
                        Layout.fillWidth: true
                        model: SettingsManager.keyOptions
                        currentIndex: SettingsManager.keyIndex
                        onCurrentIndexChanged: SettingsManager.keyIndex = currentIndex
                    }
                    
                    Label {
                        text: SettingsManager.keyDescription
                        font.pixelSize: 12
                        opacity: 0.6
                        font.italic: true
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Material.dividerColor
            }

            // Advanced Section
            Pane {
                Layout.fillWidth: true
                padding: 20

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 16

                    Label {
                        text: { Translator.langCode; return Translator.tr("advanced") }
                        font.pixelSize: 14
                        font.weight: Font.Medium
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            
                            Label {
                                text: { Translator.langCode; return Translator.tr("test_mode") }
                                font.pixelSize: 14
                            }
                            
                            Label {
                                text: { Translator.langCode; return Translator.tr("test_mode_desc") }
                                font.pixelSize: 12
                                opacity: 0.6
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                        
                        Switch {
                            id: testModeSwitch
                            checked: SettingsManager.testMode
                            onCheckedChanged: SettingsManager.testMode = checked
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Material.dividerColor
            }

            // Reset Section
            Pane {
                Layout.fillWidth: true
                padding: 20

                Button {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: { Translator.langCode; return Translator.tr("reset_defaults") }
                    flat: true
                    Material.foreground: Material.Red
                    onClicked: SettingsManager.resetToDefaults()
                }
            }

            Item { Layout.preferredHeight: 24 }
        }
    }
}
