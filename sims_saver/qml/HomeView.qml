import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#F8FAFC"
    
    signal settingsRequested()
    
    // Color palette
    readonly property color primaryColor: "#6366F1"
    readonly property color cardColor: "#FFFFFF"
    readonly property color textColor: "#1E293B"
    readonly property color textSecondaryColor: "#64748B"
    readonly property color successColor: "#10B981"
    readonly property color warningColor: "#F59E0B"
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
                anchors.leftMargin: 16
                anchors.rightMargin: 8
                
                Text {
                    text: qsTr("Sims 4 Save Helper")
                    font.pixelSize: 18
                    font.weight: Font.Medium
                    color: "white"
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "\u2699"
                    font.pixelSize: 20
                    flat: true
                    onClicked: root.settingsRequested()
                    
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
            }
        }

        // Content area
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 24

                // Status card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: statusColumn.implicitHeight + 40
                    color: cardColor
                    radius: 8
                    border.color: "#E2E8F0"
                    border.width: 1

                    ColumnLayout {
                        id: statusColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: qsTr("Status")
                            font.pixelSize: 12
                            font.weight: Font.Medium
                            color: textSecondaryColor
                        }

                        Row {
                            spacing: 12
                            
                            Rectangle {
                                width: 12
                                height: 12
                                radius: 6
                                anchors.verticalCenter: parent.verticalCenter
                                color: AppController.isRunning ? 
                                    (AppController.processDetected ? successColor : warningColor) : 
                                    textSecondaryColor
                            }
                            
                            Text {
                                text: AppController.statusText
                                font.pixelSize: 16
                                color: textColor
                                wrapMode: Text.WordWrap
                            }
                        }

                        Text {
                            visible: AppController.isRunning && !AppController.processDetected
                            text: qsTr("Waiting for The Sims 4 to start...")
                            font.pixelSize: 13
                            color: textSecondaryColor
                            font.italic: true
                        }
                    }
                }

                // Current settings summary
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: settingsColumn.implicitHeight + 32
                    color: cardColor
                    radius: 8
                    border.color: "#E2E8F0"
                    border.width: 1

                    ColumnLayout {
                        id: settingsColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 16
                        spacing: 8

                        Text {
                            text: qsTr("Current Settings")
                            font.pixelSize: 12
                            font.weight: Font.Medium
                            color: textSecondaryColor
                        }

                        Text {
                            text: qsTr("Interval: %1").arg(SettingsManager.intervalDisplayText)
                            font.pixelSize: 14
                            color: textColor
                        }

                        Text {
                            text: qsTr("Key: %1").arg(SettingsManager.keyDisplayText)
                            font.pixelSize: 14
                            color: textColor
                        }
                    }
                }

                Item { Layout.fillHeight: true }

                // Action button
                Button {
                    id: actionButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: 56
                    
                    background: Rectangle {
                        color: AppController.isRunning ? errorColor : primaryColor
                        radius: 8
                        
                        Rectangle {
                            anchors.fill: parent
                            color: "black"
                            opacity: actionButton.pressed ? 0.2 : (actionButton.hovered ? 0.1 : 0)
                            radius: parent.radius
                        }
                    }
                    
                    contentItem: Text {
                        text: AppController.isRunning ? qsTr("Stop Helper") : qsTr("Start Helper")
                        font.pixelSize: 16
                        font.weight: Font.Medium
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        if (AppController.isRunning) {
                            AppController.stop()
                        } else {
                            AppController.start()
                        }
                    }
                }

                // Info text
                Text {
                    Layout.fillWidth: true
                    text: qsTr("This app will press your selected key when The Sims 4 is running to remind you to save.")
                    font.pixelSize: 12
                    color: textSecondaryColor
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }
    }
}
