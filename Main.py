import sys
import Shunt
import GUI
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    # start shunt
    s = Shunt.Shunt()
    Thread(target=s.run).start()

    # start gui and show MainWindow
    app = QApplication(sys.argv)
    c = GUI.GuiThread()
    Thread(target=c.run).start()
    c.show()
    sys.exit(app.exec_())