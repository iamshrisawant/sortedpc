# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LogRow.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QSizePolicy, QWidget)

class Ui_LogRow(object):
    def setupUi(self, LogRow):
        if not LogRow.objectName():
            LogRow.setObjectName(u"LogRow")
        self.logRowLayout = QHBoxLayout(LogRow)
        self.logRowLayout.setObjectName(u"logRowLayout")
        self.lblFilename = QLabel(LogRow)
        self.lblFilename.setObjectName(u"lblFilename")

        self.logRowLayout.addWidget(self.lblFilename)

        self.cbPathSuggestions = QComboBox(LogRow)
        self.cbPathSuggestions.addItem("")
        self.cbPathSuggestions.addItem("")
        self.cbPathSuggestions.setObjectName(u"cbPathSuggestions")
        self.cbPathSuggestions.setEditable(True)

        self.logRowLayout.addWidget(self.cbPathSuggestions)


        self.retranslateUi(LogRow)

        QMetaObject.connectSlotsByName(LogRow)
    # setupUi

    def retranslateUi(self, LogRow):
        self.lblFilename.setText(QCoreApplication.translate("LogRow", u"TextLabel", None))
        self.cbPathSuggestions.setItemText(0, QCoreApplication.translate("LogRow", u"predictions", None))
        self.cbPathSuggestions.setItemText(1, QCoreApplication.translate("LogRow", u"Other...", None))

        pass
    # retranslateUi

