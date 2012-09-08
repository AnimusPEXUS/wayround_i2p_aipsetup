import os.path
import glob

import PyQt4.uic
import PyQt4.QtGui
import PyQt4.QtCore

import org.wayround.utils.text

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config



class MainWindow:

    def __init__(self, config, no_loop):

        self.config = config

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'latest_edit.ui'
            )

        if not no_loop:
            self.app = PyQt4.QtGui.QApplication([])

        self.window = PyQt4.uic.loadUi(ui_file)


        self.window.listWidget.itemActivated.connect(
            self.onListItemActivated
            )

        self.window.pushButton_3.clicked.connect(
            self.onReloadListButtonActivated
            )

        self.window.show()
        self.load_list()

        self.currently_opened = ''

    def load_list(self):

        db = org.wayround.aipsetup.pkgindex.PackageDatabase()

        lst = db.get_list_of_non_automatic_package_info()

        lst.sort(key=lambda i: i['name'])

        del db

        self.window.listWidget.clear()
        for i in lst:
            self.window.listWidget.addItem(i['name'])

    def load_item(self, name):
        db = org.wayround.aipsetup.pkgindex.PackageDatabase()

        self.window.setWindowTitle(name)
        self.window.lineEdit_3.setText(name)

        info = db.package_info_record_to_dict(name)

        self.window.label.setEnabled(not info['auto_newest_src'])
        self.window.lineEdit_2.setEnabled(not info['auto_newest_src'])
        self.window.listWidget_2.setEnabled(not info['auto_newest_src'])

        self.window.label_2.setEnabled(not info['auto_newest_pkg'])
        self.window.lineEdit.setEnabled(not info['auto_newest_pkg'])
        self.window.listWidget_3.setEnabled(not info['auto_newest_pkg'])

        del db

        return 0

    def wait(self):
        return self.app.exec_()

    def close(self):
        self.app.quit()
        return

    def onReloadListButtonActivated(self, toggle):
        self.load_list()

    def onListItemActivated(self, item):
        self.load_item(item.text())

def main(name_to_edit=None, no_loop=False):
    mw = MainWindow(org.wayround.aipsetup.config.config, no_loop)

    if isinstance(name_to_edit, str):
        if mw.load_item(name_to_edit) != 0:
            mw.close()
        else:
            if not no_loop:
                mw.wait()
    else:
        if not no_loop:
            mw.wait()

    return


