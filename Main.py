import sys
import Shunt
import GUI
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    # start shunt
    s = Shunt.Shunt()
    Thread(target=s.run).start()

    # 把这一长串写成一个函数，像上面一样，不然太丑陋了
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    c = GUI.GuiThread()
    c.setupUi(MainWindow)
    c.connect.clicked.connect(c.connect_button_click)
    c.disconnect.clicked.connect(c.disconnect_button_click)
    c.txt_signal.connect(c.writetoTextbox)
    c.init()
    Thread(target=c.run).start()
    MainWindow.show()
    sys.exit(app.exec_())