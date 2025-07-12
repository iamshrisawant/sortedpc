# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'logWindow.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QLabel, QListWidget, QListWidgetItem,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_logWindow(object):
    def setupUi(self, logWindow):
        if not logWindow.objectName():
            logWindow.setObjectName(u"logWindow")
        logWindow.resize(500, 300)
        logWindow.setMinimumSize(QSize(500, 300))
        self.widget = QWidget(logWindow)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 10, 481, 281))
        self.verticalLayoutWidget = QWidget(self.widget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 481, 281))
        self.logLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.logLayout.setObjectName(u"logLayout")
        self.logLayout.setContentsMargins(0, 0, 0, 0)
        self.labelLog = QLabel(self.verticalLayoutWidget)
        self.labelLog.setObjectName(u"labelLog")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelLog.sizePolicy().hasHeightForWidth())
        self.labelLog.setSizePolicy(sizePolicy)

        self.logLayout.addWidget(self.labelLog)

        self.lwLog = QListWidget(self.verticalLayoutWidget)
        self.lwLog.setObjectName(u"lwLog")
        self.lwLog.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.SelectedClicked)
        self.lwLog.setAlternatingRowColors(True)

        self.logLayout.addWidget(self.lwLog)

        self.bbButtons = QDialogButtonBox(self.verticalLayoutWidget)
        self.bbButtons.setObjectName(u"bbButtons")
        self.bbButtons.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Reset)

        self.logLayout.addWidget(self.bbButtons)


        self.retranslateUi(logWindow)

        QMetaObject.connectSlotsByName(logWindow)
    # setupUi

    def retranslateUi(self, logWindow):
        logWindow.setWindowTitle(QCoreApplication.translate("logWindow", u"Dialog", None))
        self.labelLog.setText(QCoreApplication.translate("logWindow", u"Actions Log :", None))
#if QT_CONFIG(tooltip)
        self.lwLog.setToolTip(QCoreApplication.translate("logWindow", u"\"List of sorter/LLM?RAG actions and predictions\"", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

