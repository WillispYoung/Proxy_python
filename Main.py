import sys
import Shunt
# import GUI
from threading import Thread
# from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    # start shunt
    s = Shunt.Shunt()
    shunt_thread = Thread(target=s.run)
    shunt_thread.setDaemon(True)
    shunt_thread.start()

    # start gui and show MainWindow
    # app = QApplication(sys.argv)
    # c = GUI.GuiThread()
    #
    # gui_thread = Thread(target=c.run)
    # gui_thread.setDaemon(True)
    # gui_thread.start()
    #
    # c.show()
    # sys.exit(app.exec_())
