
import os.path
import glob

import PyQt4.uic
import PyQt4.QtGui
import PyQt4.QtCore

import org.wayround.utils.text

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config

__file__ == os.path.abspath(__file__)

class MainWindow:

    def __init__(self, config):

        self.config = config

        dir = os.path.dirname(__file__)
        ui_file = os.path.join(dir, 'ui', 'info_edit.ui')

        self.app = PyQt4.QtGui.QApplication([])

        self.window = PyQt4.uic.loadUi(ui_file)

        self.window.listWidget.itemActivated.connect(
            self.onListItemActivated
            )

        self.window.pushButton_5.clicked.connect(
            self.onSaveButtonActivated
            )

        self.window.pushButton_6.clicked.connect(
            self.onRevertButtonActivated
            )

        self.window.show()
        self.load_list()

        self.currently_opened = ''

        #PyQt4.QtGui.QMessageBox.information(
            #self.window, 'About', 'This is cool program'
            #)

    def load_data(self, name):

        ret = 0

        filename = os.path.join(
            self.config['info'],
            '%(name)s' % {
                'name': name
                }
            )

        if not os.path.isfile(filename):
            PyQt4.QtGui.QMessageBox.critical(
                self.window, 'Error', 'File not exists'
                )
            ret = 1
        else:
            data = org.wayround.aipsetup.info.read_from_file(filename)

            if not isinstance(data, dict):
                PyQt4.QtGui.QMessageBox.critical(
                    self.window, 'Error', "Can't read data from file"
                    )
                ret = 1
            else:
                self.window.lineEdit.setText(data['homepage'])
                self.window.plainTextEdit.setPlainText(data['description'])
                self.window.lineEdit_2.setText(data['pkg_name_type'])
                self.window.plainTextEdit_4.setPlainText(
                    '\n'.join(data['tags']) + '\n'
                    )

        return ret

    def save_data(self, name):

        ret = 0

        filename = os.path.join(
            self.config['info'],
            '%(name)s' % {
                'name': name
                }
            )

        data = {}
        data['homepage'] = str(self.window.lineEdit.text()).strip()
        data['description'] = str(self.window.plainTextEdit.toPlainText())
        data['pkg_name_type'] = str(self.window.lineEdit_2.text()).strip()
        data['buildinfo'] = str(self.window.lineEdit_3.text()).strip()

        data['tags'] = org.wayround.utils.text.strip_remove_empty_remove_duplicated_lines(
            str(self.window.plainTextEdit_4.toPlainText()).splitlines()
            )

        if org.wayround.aipsetup.info.write_to_file(filename, data) != 0:
            PyQt4.QtGui.QMessageBox.critical(
                self.window, 'Error',
                "Can't save to file %(name)s" % {
                    'name': filename
                    }
                )
            ret = 1
        else:
            PyQt4.QtGui.QMessageBox.information(
                self.window, 'Success', 'File saved'
                )


        return ret

    def onRevertButtonActivated(self, toggle):
        if self.load_data(self.currently_opened) != 0:
            PyQt4.QtGui.QMessageBox.critical(
                self.window, 'Error', "Can't reread file"
                )
        else:
            PyQt4.QtGui.QMessageBox.information(
                self.window, 'Success', 'Canceled changes'
                )

    def onSaveButtonActivated(self, toggle):
        self.save_data(self.currently_opened)

    def onListItemActivated(self, item):
        #PyQt4.QtGui.QMessageBox.information(
            #self.window, 'About', 'Activated %(name)s' % {
                #'name': item.text()
                #}
            #)

        self.load_data(item.text())
        self.currently_opened = item.text()
        self.window.setWindowTitle(item.text())

    def load_list(self):

        mask = os.path.join(self.config['info'], '*.xml')

        files = glob.glob(mask)

        files.sort()

        for i in files:
            base = os.path.basename(i)

            self.window.listWidget.addItem(base)

    def wait(self):
        return self.app.exec_()

def main():
    mw = MainWindow(org.wayround.aipsetup.config.config)
    return mw.wait()
