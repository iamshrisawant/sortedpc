# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(398, 450)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 10, 381, 431))
        self.verticalLayoutWidget = QWidget(self.widget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, -1, 381, 431))
        self.configLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.configLayout.setObjectName(u"configLayout")
        self.configLayout.setContentsMargins(0, 0, 0, 0)
        self.labelKBPaths = QLabel(self.verticalLayoutWidget)
        self.labelKBPaths.setObjectName(u"labelKBPaths")

        self.configLayout.addWidget(self.labelKBPaths)

        self.lwKBPaths = QListWidget(self.verticalLayoutWidget)
        self.lwKBPaths.setObjectName(u"lwKBPaths")
        self.lwKBPaths.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lwKBPaths.setAlternatingRowColors(True)
        self.lwKBPaths.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.configLayout.addWidget(self.lwKBPaths)

        self.line_3 = QFrame(self.verticalLayoutWidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.configLayout.addWidget(self.line_3)

        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.configLayout.addWidget(self.label_4)

        self.lwWatch = QListWidget(self.verticalLayoutWidget)
        self.lwWatch.setObjectName(u"lwWatch")
        self.lwWatch.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lwWatch.setAlternatingRowColors(True)
        self.lwWatch.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.configLayout.addWidget(self.lwWatch)

        self.line_2 = QFrame(self.verticalLayoutWidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.configLayout.addWidget(self.line_2)

        self.themeLayout = QHBoxLayout()
        self.themeLayout.setObjectName(u"themeLayout")
        self.labelTheme = QLabel(self.verticalLayoutWidget)
        self.labelTheme.setObjectName(u"labelTheme")

        self.themeLayout.addWidget(self.labelTheme)

        self.cbTheme = QComboBox(self.verticalLayoutWidget)
        self.cbTheme.addItem("")
        self.cbTheme.addItem("")
        self.cbTheme.addItem("")
        self.cbTheme.setObjectName(u"cbTheme")

        self.themeLayout.addWidget(self.cbTheme)


        self.configLayout.addLayout(self.themeLayout)

        self.positionLayout = QHBoxLayout()
        self.positionLayout.setObjectName(u"positionLayout")
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.positionLayout.addWidget(self.label)

        self.cbLaunchPos = QComboBox(self.verticalLayoutWidget)
        self.cbLaunchPos.addItem("")
        self.cbLaunchPos.addItem("")
        self.cbLaunchPos.addItem("")
        self.cbLaunchPos.setObjectName(u"cbLaunchPos")

        self.positionLayout.addWidget(self.cbLaunchPos)


        self.configLayout.addLayout(self.positionLayout)

        self.line = QFrame(self.verticalLayoutWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.configLayout.addWidget(self.line)

        self.bbButtons = QDialogButtonBox(self.verticalLayoutWidget)
        self.bbButtons.setObjectName(u"bbButtons")
        self.bbButtons.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.RestoreDefaults|QDialogButtonBox.StandardButton.Save)

        self.configLayout.addWidget(self.bbButtons)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.labelKBPaths.setText(QCoreApplication.translate("Dialog", u"KB Paths:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Watch Folders:", None))
        self.labelTheme.setText(QCoreApplication.translate("Dialog", u"UI Theme :", None))
        self.cbTheme.setItemText(0, QCoreApplication.translate("Dialog", u"System", None))
        self.cbTheme.setItemText(1, QCoreApplication.translate("Dialog", u"Light", None))
        self.cbTheme.setItemText(2, QCoreApplication.translate("Dialog", u"Dark", None))

        self.label.setText(QCoreApplication.translate("Dialog", u"Launch Position :", None))
        self.cbLaunchPos.setItemText(0, QCoreApplication.translate("Dialog", u"Left Center", None))
        self.cbLaunchPos.setItemText(1, QCoreApplication.translate("Dialog", u"Center", None))
        self.cbLaunchPos.setItemText(2, QCoreApplication.translate("Dialog", u"Right Center", None))

    # retranslateUi

