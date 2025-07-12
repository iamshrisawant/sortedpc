# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PathRow.ui'
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

class Ui_PathRow(object):
    def setupUi(self, PathRow):
        if not PathRow.objectName():
            PathRow.setObjectName(u"PathRow")
        self.horizontalLayout = QHBoxLayout(PathRow)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(PathRow)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.toolButton = QToolButton(PathRow)
        self.toolButton.setObjectName(u"toolButton")
        icon = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.toolButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButton)


        self.retranslateUi(PathRow)

        QMetaObject.connectSlotsByName(PathRow)
    # setupUi

    def retranslateUi(self, PathRow):
        self.label.setText(QCoreApplication.translate("PathRow", u"TextLabel", None))
        pass
    # retranslateUi

