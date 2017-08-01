from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.Qt import *
import time
from threading import Thread
import socket
import json


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 600)
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
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(100, -1, 100, -1)
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
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
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
        self.listWidget.setFont(QFont("微软雅黑", 10))
        self.connect.setFont(QFont("微软雅黑", 10))
        self.disconnect.setFont(QFont("微软雅黑", 10))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def writetoTextbox(self, item):
        self.listWidget.addItem(item)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tsinghua WiFi-VPN Tunnel"))
        self.label.setText(_translate("MainWindow", "Current State:"))
        self.groupBox.setTitle(_translate("MainWindow", "Operations"))
        self.connect.setText(_translate("MainWindow", "Connect"))
        self.disconnect.setText(_translate("MainWindow", "Disconnect"))


class GuiThread(QtWidgets.QMainWindow, Ui_MainWindow):
    txt_signal = pyqtSignal(QtWidgets.QListWidgetItem)
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.close_flag = 0
        self.connect.clicked.connect(self.connect_button_click)
        self.disconnect.clicked.connect(self.disconnect_button_click)
        self.txt_signal.connect(self.writetoTextbox)

        self.listWidget.addItem(QtWidgets.QListWidgetItem("欢迎使用清云WiFiVPN安全通道\n"
                             "在启动连接之前，请将本机的网络代理设置成本地的6666端口\n"
                             "之后点击 Connect 按钮，安全通道即可开始工作\n"
                             "----------------------------------"))
        try:
            data = json.load(open("init/config.json"))
            self.backend_addr = ("localhost", data["shunt"]["event_listen_port"])
            self.listen_addr = ("localhost", data["GUI"]["listen_port"])
            self.listWidget.addItem(QtWidgets.QListWidgetItem("Configuration file loaded, program ready."))
        except IOError:
            self.listWidget.addItem(QtWidgets.QListWidgetItem("config file not found"))
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
                output = QtWidgets.QListWidgetItem(content[0:50] + "...")
                tmp = 0
                tipcontent = ""
                while True:
                    if (tmp+1)*50 >= len(content):
                        tipcontent += content[(tmp * 50):]
                        break
                    tipcontent += content[(tmp*50):((tmp+1)*50)] + "\n"
                    tmp+=1
                output.setToolTip(tipcontent)
                self.txt_signal.emit(output)
            except socket.error:
                gui.close()

    def connect_button_click(self):
        self.state.setText("Connected")
        self.txt_signal.emit(QtWidgets.QListWidgetItem("WiFi-VPN Tunnel connected."))
        try:
            s = self.generate_socket(self.backend_addr)
            s.send(bytes("connect", encoding="utf-8"))
            s.close()
        except socket.error:
            pass
            print("failed in sending control message")

    def disconnect_button_click(self):
        self.state.setText("Disconnected")
        self.txt_signal.emit(QtWidgets.QListWidgetItem("WiFi-VPN Tunnel disconnected."))
        try:
            s = self.generate_socket(self.backend_addr)
            s.send(bytes("disconnect", encoding="utf-8"))
            s.close()
        except socket.error:
            pass
            print("failed in sending control message")

    @staticmethod
    def generate_socket(addr):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        return s

    def closeEvent(self, event):
        self.message = QMessageBox.question(self, u'提示:', u'你确认要退出？', QMessageBox.Yes | QMessageBox.No)
        if self.message == QMessageBox.Yes:
            print("program exit now")
            event.accept()
        else:
            event.ignore()

