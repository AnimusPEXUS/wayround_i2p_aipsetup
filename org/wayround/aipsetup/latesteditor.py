import os.path
import glob

import PyQt4.uic
import PyQt4.QtGui

import org.wayround.utils.text

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config



class MainWindow:

    def __init__(self, config):

        self.config = config

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'latest_edit.ui'
            )

        self.app = PyQt4.QtGui.QApplication([])

        self.window = PyQt4.uic.loadUi(ui_file)


        self.window.show()
        self.load_list()

        self.currently_opened = ''

    def load_list(self):

        db = org.wayround.aipsetup.pkgindex.PackageDatabase()

        lst = db.get_list_of_non_automatic_package_info()

        lst.sort(key=lambda i:  i['name'])

        del db

        self.window.listWidget.clear()
        for i in lst:
            self.window.listWidget.addItem(i['name'])

    def wait(self):
        return self.app.exec_()

    def close(self):
        self.app.quit()
        return


def main(file_to_edit=None):
    mw = MainWindow(org.wayround.aipsetup.config.config)

    if isinstance(file_to_edit, str):
        if mw.load_data(os.path.basename(file_to_edit)) != 0:
            mw.close()
        else:
            mw.wait()
    else:
        mw.wait()

    return
