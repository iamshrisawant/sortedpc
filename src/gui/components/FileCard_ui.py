# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FileCard.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QToolButton, QWidget)

class Ui_FileCard(object):
    def setupUi(self, FileCard):
        if not FileCard.objectName():
            FileCard.setObjectName(u"FileCard")
        self.cardLayout = QHBoxLayout(FileCard)
        self.cardLayout.setObjectName(u"cardLayout")
        self.btnOpen = QToolButton(FileCard)
        self.btnOpen.setObjectName(u"btnOpen")
        icon = QIcon(QIcon.fromTheme(u"document-open"))
        self.btnOpen.setIcon(icon)
        self.btnOpen.setIconSize(QSize(24, 24))

        self.cardLayout.addWidget(self.btnOpen)

        self.lblFileName = QLabel(FileCard)
        self.lblFileName.setObjectName(u"lblFileName")

        self.cardLayout.addWidget(self.lblFileName)

        self.btnClose = QToolButton(FileCard)
        self.btnClose.setObjectName(u"btnClose")
        icon1 = QIcon(QIcon.fromTheme(u"application-exit"))
        self.btnClose.setIcon(icon1)
        self.btnClose.setIconSize(QSize(12, 12))

        self.cardLayout.addWidget(self.btnClose)


        self.retranslateUi(FileCard)

        QMetaObject.connectSlotsByName(FileCard)
    # setupUi

    def retranslateUi(self, FileCard):
        self.lblFileName.setText(QCoreApplication.translate("FileCard", u"TextLabel", None))
        pass
    # retranslateUi

