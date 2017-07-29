import sys
import shunt
import gui
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    #shunt
    c = gui.GuiThread()
    c.setupUi(MainWindow)
    c.connect.clicked.connect(c.connect_button_click)
    c.disconnect.clicked.connect(c.disconnect_button_click)
    c.txt_signal.connect(c.writetoTextbox)
    # shunt thread start here
    c.init()
    Thread(target=c.start).start()
    MainWindow.show()
    sys.exit(app.exec_())