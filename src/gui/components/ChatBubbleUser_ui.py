# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ChatBubbleUser.ui'
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

class Ui_ChatBubbleUser(object):
    def setupUi(self, ChatBubbleUser):
        if not ChatBubbleUser.objectName():
            ChatBubbleUser.setObjectName(u"ChatBubbleUser")
        self.bubbleLayout = QHBoxLayout(ChatBubbleUser)
        self.bubbleLayout.setObjectName(u"bubbleLayout")
        self.labelMessage = QLabel(ChatBubbleUser)
        self.labelMessage.setObjectName(u"labelMessage")
        self.labelMessage.setMinimumSize(QSize(100, 0))
        self.labelMessage.setMaximumSize(QSize(400, 16777215))
        self.labelMessage.setWordWrap(True)

        self.bubbleLayout.addWidget(self.labelMessage)


        self.retranslateUi(ChatBubbleUser)

        QMetaObject.connectSlotsByName(ChatBubbleUser)
    # setupUi

    def retranslateUi(self, ChatBubbleUser):
        self.labelMessage.setText(QCoreApplication.translate("ChatBubbleUser", u"TextLabel", None))
        pass
    # retranslateUi

