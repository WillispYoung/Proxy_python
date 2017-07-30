from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
import subprocess
from threading import Thread
import socket
import json


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
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
        self.label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.state.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.groupBox.setFont(QFont("微软雅黑", 10))
        self.textEdit.setFont(QFont("微软雅黑", 10))
        self.connect.setFont(QFont("微软雅黑", 10))
        self.disconnect.setFont(QFont("微软雅黑", 10))
        self.cancel.setFont(QFont("微软雅黑", 10))
        self.cancel.clicked.connect(QtCore.QCoreApplication.quit)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def writetoTextbox(self, text):
        self.textEdit.append(text)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tsinghua WiFi-VPN Tunnel"))
        self.label.setText(_translate("MainWindow", "Current State:"))
        self.groupBox.setTitle(_translate("MainWindow", "Operations"))
        self.connect.setText(_translate("MainWindow", "Connect"))
        self.disconnect.setText(_translate("MainWindow", "Disconnect"))
        self.cancel.setText(_translate("MainWindow", "Cancel"))


class GuiThread(QtWidgets.QMainWindow, Ui_MainWindow):
    txt_signal = pyqtSignal(str)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.close_flag = 0
        self.connect.clicked.connect(self.connect_button_click)
        self.disconnect.clicked.connect(self.disconnect_button_click)
        self.txt_signal.connect(self.writetoTextbox)
        self.textEdit.append("Welcome to use Tsinghua WiFi-VPN Tunnel.")
        self.textEdit.append("Before you press the Connect button please set the proxy server port to 6666.")
        self.textEdit.append("")
        try:
            data = json.load(open("init/config.json"))
            self.backend_addr = ("localhost", data["shunt"]["event_listen_port"])
            self.listen_addr = ("localhost", data["GUI"]["listen_port"])
            self.textEdit.append("config information loaded")
        except IOError:
            self.textEdit.append("config file not found")
            exit(1)

        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor.bind(self.listen_addr)
        self.acceptor.listen(20)

    def run(self):
        while True:
            gui, _ = self.acceptor.accept()
            try:
                msg = gui.recv(4096)
                content = msg.decode("utf-8")
                self.txt_signal.emit(content)
            except socket.error:
                gui.close()

    # cancel按钮的有作用吗？另外，要设置成点击右上角关闭后程序退出（exit(0)）

    def connect_button_click(self):
        self.state.setText("Connected")
        self.txt_signal.emit("WiFi-VPN Tunnel connected.")
        try:
            s = self.generate_socket(self.backend_addr)
            s.send(bytes("connect", encoding="utf-8"))
            s.close()
        except socket.error:
            print("failed in sending control message")

    def disconnect_button_click(self):
        self.state.setText("Disconnected")
        self.txt_signal.emit("WiFi-VPN Tunnel disconnected.")
        try:
            s = self.generate_socket(self.backend_addr)
            s.send(bytes("disconnect", encoding="utf-8"))
            s.close()
        except socket.error:
            print("failed in sending control message")

    @staticmethod
    def generate_socket(addr):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        return s

    def closeEvent(self, event):
        print("close!!!")
        #这里处理右上角关闭事件，exit（0）会无响应，用socket发给后台信息，后台进行break,exit都没有用


