import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#F8FAFC"
    
    signal backRequested()
    
    // Color palette
    readonly property color primaryColor: "#6366F1"
    readonly property color cardColor: "#FFFFFF"
    readonly property color textColor: "#1E293B"
    readonly property color textSecondaryColor: "#64748B"
    readonly property color errorColor: "#EF4444"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 56
            color: primaryColor
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 4
                anchors.rightMargin: 16
                
                Button {
                    text: "\u2190"
                    font.pixelSize: 20
                    flat: true
                    onClicked: root.backRequested()
                    
                    background: Rectangle {
                        color: parent.hovered ? Qt.rgba(1,1,1,0.2) : "transparent"
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                
                Text {
                    text: qsTr("Settings")
                    font.pixelSize: 18
                    font.weight: Font.Medium
                    color: "white"
                    Layout.fillWidth: true
                }
            }
        }

        // Scrollable content
        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: width
            contentHeight: contentColumn.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ColumnLayout {
                id: contentColumn
                width: parent.width
                spacing: 0

                // Interval Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: intervalColumn.implicitHeight + 40
                    color: cardColor

                    ColumnLayout {
                        id: intervalColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: qsTr("Save Interval")
                            font.pixelSize: 14
                            font.weight: Font.Medium
                            color: textColor
                        }

                        Text {
                            text: qsTr("How often should the helper press the save key?")
                            font.pixelSize: 12
                            color: textSecondaryColor
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
                    Layout.preferredHeight: 1
                    color: "#E2E8F0"
                }

                // Key Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: keyColumn.implicitHeight + 40
                    color: cardColor

                    ColumnLayout {
                        id: keyColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: qsTr("Key to Press")
                            font.pixelSize: 14
                            font.weight: Font.Medium
                            color: textColor
                        }

                        Text {
                            text: qsTr("Which key should be pressed to trigger save?")
                            font.pixelSize: 12
                            color: textSecondaryColor
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
                        
                        Text {
                            text: SettingsManager.keyDescription
                            font.pixelSize: 12
                            color: textSecondaryColor
                            font.italic: true
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: "#E2E8F0"
                }

                // Language Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: langColumn.implicitHeight + 40
                    color: cardColor

                    ColumnLayout {
                        id: langColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: qsTr("Language")
                            font.pixelSize: 14
                            font.weight: Font.Medium
                            color: textColor
                        }

                        ComboBox {
                            id: languageCombo
                            Layout.fillWidth: true
                            model: SettingsManager.languageOptions
                            currentIndex: SettingsManager.languageIndex
                            onCurrentIndexChanged: SettingsManager.languageIndex = currentIndex
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: "#E2E8F0"
                }

                // Advanced Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: advancedColumn.implicitHeight + 40
                    color: cardColor

                    ColumnLayout {
                        id: advancedColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 20
                        spacing: 16

                        Text {
                            text: qsTr("Advanced")
                            font.pixelSize: 14
                            font.weight: Font.Medium
                            color: textColor
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                
                                Text {
                                    text: qsTr("Test Mode")
                                    font.pixelSize: 14
                                    color: textColor
                                }
                                
                                Text {
                                    text: qsTr("Press keys even when The Sims 4 is not running")
                                    font.pixelSize: 12
                                    color: textSecondaryColor
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
                    Layout.preferredHeight: 1
                    color: "#E2E8F0"
                }

                // Reset Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    color: cardColor

                    Button {
                        anchors.centerIn: parent
                        text: qsTr("Reset to Defaults")
                        flat: true
                        
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: errorColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        background: Rectangle {
                            color: parent.hovered ? Qt.rgba(239/255, 68/255, 68/255, 0.1) : "transparent"
                            radius: 4
                        }
                        
                        onClicked: SettingsManager.resetToDefaults()
                    }
                }

                Item { Layout.preferredHeight: 24 }
            }
        }
    }
}
