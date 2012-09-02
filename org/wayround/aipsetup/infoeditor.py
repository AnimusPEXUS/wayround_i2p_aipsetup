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
            os.path.dirname(__file__), 'ui', 'info_edit.ui'
            )

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

        self.window.pushButton.clicked.connect(
            self.onSaveAndUpdateButtonActivated
            )

        self.window.pushButton_2.clicked.connect(
            self.onListRealoadButtonActivated
            )

        self.window.show()
        self.load_list()

        self.currently_opened = ''


    def load_data(self, name):

        ret = 0

        self.window.setEnabled(False)
        self.window.repaint()

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

                self.window.lineEdit_7.setText(name)
                self.window.plainTextEdit.setPlainText(data['description'])
                self.window.lineEdit.setText(data['home_page'])

                self.window.plainTextEdit_4.setPlainText(
                    '\n'.join(data['tags']) + '\n'
                    )

                self.window.lineEdit_3.setText(data['buildinfo'])
                self.window.lineEdit_2.setText(data['basename'])
                self.window.lineEdit_4.setText(data['version_re'])
                self.window.spinBox.setValue(data['installation_priority'])
                self.window.checkBox.setChecked(bool(data['deletable']))
                self.window.checkBox_2.setChecked(bool(data['updatable']))
                self.window.checkBox_3.setChecked(bool(data['auto_newest_src']))
                self.window.checkBox_4.setChecked(bool(data['auto_newest_pkg']))

                db = org.wayround.aipsetup.pkgindex.PackageDatabase()
                self.window.lineEdit_5.setText(db.get_latest_source(name[:-4]))
                self.window.lineEdit_6.setText(db.get_latest_package(name[:-4]))
                del db

                self.currently_opened = name
                self.window.setWindowTitle(name + " - aipsetup v3 .xml info file editor")


        self.window.setEnabled(True)

        return ret

    def save_data(self, name, update_db=False):

        ret = 0

        filename = os.path.join(
            self.config['info'],
            '%(name)s' % {
                'name': name
                }
            )

        data = {}
        data['description'] = str(self.window.plainTextEdit.toPlainText())
        data['home_page'] = str(self.window.lineEdit.text()).strip()

        data['tags'] = org.wayround.utils.text.strip_remove_empty_remove_duplicated_lines(
            str(self.window.plainTextEdit_4.toPlainText()).splitlines()
            )

        data['buildinfo'] = str(self.window.lineEdit_3.text()).strip()
        data['basename'] = str(self.window.lineEdit_2.text()).strip()
        data['version_re'] = str(self.window.lineEdit_4.text()).strip()
        data['installation_priority'] = self.window.spinBox.value()
        data['deletable'] = self.window.checkBox.isChecked()
        data['updatable'] = self.window.checkBox_2.isChecked()
        data['auto_newest_src'] = self.window.checkBox_3.isChecked()
        data['auto_newest_pkg'] = self.window.checkBox_4.isChecked()


        if org.wayround.aipsetup.info.write_to_file(filename, data) != 0:
            PyQt4.QtGui.QMessageBox.critical(
                self.window, 'Error',
                "Can't save to file %(name)s" % {
                    'name': filename
                    }
                )
            ret = 1
        else:

            dbu = ''
            if update_db:
                try:
                    db = org.wayround.aipsetup.pkgindex.PackageDatabase()
                    db.load_package_info_from_filesystem(
                        [filename], rewrite_existing=True
                        )
                    del db
                    dbu = "DB updated"
                except:
                    dbu = "Some error while updating DB:"

            if dbu != '':
                dbu = '\n' + dbu

            PyQt4.QtGui.QMessageBox.information(
                self.window, 'Success', 'File saved' + dbu
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

    def onSaveAndUpdateButtonActivated(self, toggle):
        self.save_data(self.currently_opened, update_db=True)

    def onListRealoadButtonActivated(self, toggle):
        self.load_list()

    def onListItemActivated(self, item):
        #PyQt4.QtGui.QMessageBox.information(
            #self.window, 'About', 'Activated %(name)s' % {
                #'name': item.text()
                #}
            #)

        self.load_data(item.text())

    def load_list(self):

        mask = os.path.join(self.config['info'], '*.xml')

        files = glob.glob(mask)

        files.sort()

        self.window.listWidget.clear()
        for i in files:
            base = os.path.basename(i)

            self.window.listWidget.addItem(base)

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
