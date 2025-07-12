# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ChatBubbleApp.ui'
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
    QWidget)

class Ui_ChatBubbleApp(object):
    def setupUi(self, ChatBubbleApp):
        if not ChatBubbleApp.objectName():
            ChatBubbleApp.setObjectName(u"ChatBubbleApp")
        self.bubbleLayout = QHBoxLayout(ChatBubbleApp)
        self.bubbleLayout.setObjectName(u"bubbleLayout")
        self.labelMessage = QLabel(ChatBubbleApp)
        self.labelMessage.setObjectName(u"labelMessage")
        self.labelMessage.setMinimumSize(QSize(100, 0))
        self.labelMessage.setMaximumSize(QSize(400, 16777215))
        self.labelMessage.setWordWrap(True)

        self.bubbleLayout.addWidget(self.labelMessage)


        self.retranslateUi(ChatBubbleApp)

        QMetaObject.connectSlotsByName(ChatBubbleApp)
    # setupUi

    def retranslateUi(self, ChatBubbleApp):
        self.labelMessage.setText(QCoreApplication.translate("ChatBubbleApp", u"TextLabel", None))
        pass
    # retranslateUi

