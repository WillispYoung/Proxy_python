# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shunt.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
import subprocess
import socket
import json

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(619, 551)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(50, 50, 50, 50)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.state = QtWidgets.QLabel(self.centralwidget)
        self.state.setText("")
        self.state.setObjectName("state")
        self.horizontalLayout.addWidget(self.state)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(60, -1, 60, -1)
        self.horizontalLayout_2.setSpacing(60)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.connect = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connect.sizePolicy().hasHeightForWidth())
        self.connect.setSizePolicy(sizePolicy)
        self.connect.setObjectName("connect")
        self.horizontalLayout_2.addWidget(self.connect)
        self.disconnect = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.disconnect.sizePolicy().hasHeightForWidth())
        self.disconnect.setSizePolicy(sizePolicy)
        self.disconnect.setObjectName("disconnect")
        self.horizontalLayout_2.addWidget(self.disconnect)
        self.cancel = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancel.sizePolicy().hasHeightForWidth())
        self.cancel.setSizePolicy(sizePolicy)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_2.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 619, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.state.setText("Disconnected")

        self.retranslateUi(MainWindow)
        self.cancel.clicked.connect(QtCore.QCoreApplication.quit)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def writetoTextbox(self, text):
        self.textEdit.append(text)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tsinghua WiFi-VPN Program"))
        self.label.setText(_translate("MainWindow", "当前状态："))
        self.groupBox.setTitle(_translate("MainWindow", "操作"))
        self.connect.setText(_translate("MainWindow", "Connect"))
        self.disconnect.setText(_translate("MainWindow", "Disconnect"))
        self.cancel.setText(_translate("MainWindow", "Cancel"))

class GuiThread(QtCore.QThread, Ui_MainWindow):
    txt_signal = pyqtSignal(str)
    def init(self):
        try:
            data = json.load(open("init/config.json"))
            self.backendaddr = (data["shunt"]["localhost"], data["shunt"]["remote_proxy_port"])
            self.listen_addr = (data["GUI"]["localhost"], data["GUI"]["listen_port"])
            self.textEdit.append("config information loaded")
        except IOError:
            self.textEdit.append("config file not found")
            exit(1)
        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor.bind(self.listen_addr)
        self.acceptor.listen(20)
        self.sock = self.generate_socket(self.backendaddr)

    def run(self):
        while True:
            gui, _ = self.acceptor.accept()
            try:
                msg = self.sock.recv(4096)
                content = msg.decode("utf-8")
                self.txt_signal.emit(content)
            except socket.error:
                gui.close()

    def connect_button_click(self):
        self.state.setText("Connected")
        msg = "connect"
        self.sock.send(msg)

    def disconnect_button_click(self):
        self.state.setText("Disconnected")
        msg = "disconnect"
        self.sock.send(msg)

    @staticmethod
    def generate_socket(addr):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        return s


