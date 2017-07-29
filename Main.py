import sys
import Shunt
import GUI
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    # start shunt
    s = Shunt.Shunt()
    Thread(target=s.run).start()

    # start GUI
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    c = GUI.GuiThread()
    c.setupUi(MainWindow)
    c.connect.clicked.connect(c.connect_button_click)
    c.disconnect.clicked.connect(c.disconnect_button_click)
    c.txt_signal.connect(c.writetoTextbox)
    c.init()
    Thread(target=c.start).start()
    MainWindow.show()
    sys.exit(app.exec_())