# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QScrollArea, QSizePolicy, QStackedWidget,
    QTextEdit, QToolButton, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(600, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(600, 300))
        MainWindow.setMaximumSize(QSize(600, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 7, 581, 281))
        self.mainVerticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.mainVerticalLayout.setObjectName(u"mainVerticalLayout")
        self.mainVerticalLayout.setContentsMargins(6, 6, 6, 6)
        self.topNavWidget = QWidget(self.verticalLayoutWidget)
        self.topNavWidget.setObjectName(u"topNavWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.topNavWidget.sizePolicy().hasHeightForWidth())
        self.topNavWidget.setSizePolicy(sizePolicy1)
        self.topNavWidget.setMinimumSize(QSize(60, 60))
        self.verticalLayout_8 = QVBoxLayout(self.topNavWidget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.topNavLayout = QHBoxLayout()
        self.topNavLayout.setSpacing(90)
        self.topNavLayout.setObjectName(u"topNavLayout")
        self.btnConfig = QPushButton(self.topNavWidget)
        self.btnConfig.setObjectName(u"btnConfig")
        self.btnConfig.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btnConfig.sizePolicy().hasHeightForWidth())
        self.btnConfig.setSizePolicy(sizePolicy2)
        self.btnConfig.setMinimumSize(QSize(36, 36))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.btnConfig.setIcon(icon)

        self.topNavLayout.addWidget(self.btnConfig)

        self.btnLog = QPushButton(self.topNavWidget)
        self.btnLog.setObjectName(u"btnLog")
        sizePolicy2.setHeightForWidth(self.btnLog.sizePolicy().hasHeightForWidth())
        self.btnLog.setSizePolicy(sizePolicy2)
        self.btnLog.setMinimumSize(QSize(36, 36))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpenRecent))
        self.btnLog.setIcon(icon1)

        self.topNavLayout.addWidget(self.btnLog)


        self.verticalLayout_8.addLayout(self.topNavLayout)


        self.mainVerticalLayout.addWidget(self.topNavWidget)

        self.stackedChatArea = QStackedWidget(self.verticalLayoutWidget)
        self.stackedChatArea.setObjectName(u"stackedChatArea")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.chatArea = QScrollArea(self.page)
        self.chatArea.setObjectName(u"chatArea")
        self.chatArea.setGeometry(QRect(10, 10, 560, 90))
        sizePolicy.setHeightForWidth(self.chatArea.sizePolicy().hasHeightForWidth())
        self.chatArea.setSizePolicy(sizePolicy)
        self.chatArea.setMinimumSize(QSize(560, 60))
        self.chatArea.setMaximumSize(QSize(16777215, 90))
        self.chatArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chatArea.setWidgetResizable(True)
        self.chatWidget = QWidget()
        self.chatWidget.setObjectName(u"chatWidget")
        self.chatWidget.setGeometry(QRect(0, 0, 558, 88))
        self.verticalLayout_6 = QVBoxLayout(self.chatWidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.chatLayout = QVBoxLayout()
        self.chatLayout.setObjectName(u"chatLayout")

        self.verticalLayout_6.addLayout(self.chatLayout)

        self.chatArea.setWidget(self.chatWidget)
        self.stackedChatArea.addWidget(self.page)
        self.greetingPage = QWidget()
        self.greetingPage.setObjectName(u"greetingPage")
        self.verticalLayoutWidget_2 = QWidget(self.greetingPage)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(10, -1, 551, 131))
        self.greetingLayout = QVBoxLayout(self.verticalLayoutWidget_2)
        self.greetingLayout.setObjectName(u"greetingLayout")
        self.greetingLayout.setContentsMargins(0, 0, 0, 0)
        self.labelGreeting = QLabel(self.verticalLayoutWidget_2)
        self.labelGreeting.setObjectName(u"labelGreeting")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.labelGreeting.setFont(font)
        self.labelGreeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelGreeting.setWordWrap(True)

        self.greetingLayout.addWidget(self.labelGreeting)

        self.stackedChatArea.addWidget(self.greetingPage)

        self.mainVerticalLayout.addWidget(self.stackedChatArea)

        self.commandPanelWidget = QWidget(self.verticalLayoutWidget)
        self.commandPanelWidget.setObjectName(u"commandPanelWidget")
        self.commandPanelWidget.setMinimumSize(QSize(0, 60))
        self.verticalLayout_7 = QVBoxLayout(self.commandPanelWidget)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.commandPanelLayout = QHBoxLayout()
        self.commandPanelLayout.setObjectName(u"commandPanelLayout")
        self.commandPanelLayout.setContentsMargins(6, 6, 6, 6)
        self.btnAttach = QToolButton(self.commandPanelWidget)
        self.btnAttach.setObjectName(u"btnAttach")
        self.btnAttach.setMinimumSize(QSize(36, 36))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MailAttachment))
        self.btnAttach.setIcon(icon2)

        self.commandPanelLayout.addWidget(self.btnAttach)

        self.leMessage = QTextEdit(self.commandPanelWidget)
        self.leMessage.setObjectName(u"leMessage")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.leMessage.sizePolicy().hasHeightForWidth())
        self.leMessage.setSizePolicy(sizePolicy3)
        self.leMessage.setMinimumSize(QSize(0, 30))

        self.commandPanelLayout.addWidget(self.leMessage)

        self.btnSend = QToolButton(self.commandPanelWidget)
        self.btnSend.setObjectName(u"btnSend")
        self.btnSend.setMinimumSize(QSize(36, 36))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSend))
        self.btnSend.setIcon(icon3)
        self.btnSend.setIconSize(QSize(12, 12))

        self.commandPanelLayout.addWidget(self.btnSend)


        self.verticalLayout_7.addLayout(self.commandPanelLayout)


        self.mainVerticalLayout.addWidget(self.commandPanelWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.btnConfig.setToolTip(QCoreApplication.translate("MainWindow", u"Edit KB & Watchers", None))
#endif // QT_CONFIG(tooltip)
        self.btnConfig.setText(QCoreApplication.translate("MainWindow", u"Config", None))
#if QT_CONFIG(tooltip)
        self.btnLog.setToolTip(QCoreApplication.translate("MainWindow", u"Review LLM + sorter actions", None))
#endif // QT_CONFIG(tooltip)
        self.btnLog.setText(QCoreApplication.translate("MainWindow", u"Log", None))
        self.labelGreeting.setText(QCoreApplication.translate("MainWindow", u"Hello There! What're you looking for?", None))
#if QT_CONFIG(tooltip)
        self.btnAttach.setToolTip(QCoreApplication.translate("MainWindow", u"Attach file", None))
#endif // QT_CONFIG(tooltip)
        self.btnAttach.setText("")
#if QT_CONFIG(tooltip)
        self.btnSend.setToolTip(QCoreApplication.translate("MainWindow", u"Send", None))
#endif // QT_CONFIG(tooltip)
        self.btnSend.setText("")
    # retranslateUi

