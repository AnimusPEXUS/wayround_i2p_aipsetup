
import os.path
import sys

import PyQt4.uic
import PyQt4.QtGui
import PyQt4.QtCore

#__file__ == os.path.abspath(__file__)

class MainWindow:

    def __init__(self):

        dir = os.path.dirname(__file__)
        ui_file = os.path.join(dir, 'ui', 'info_edit.ui')

        self.app = PyQt4.QtGui.QApplication([])

        self.window = PyQt4.uic.loadUi(ui_file)
        self.window.setLayout(self.window.verticalLayout_5)
        self.window.show()

    def wait(self):
        return self.app.exec_()

def main():
    mw = MainWindow()
    return mw.wait()
