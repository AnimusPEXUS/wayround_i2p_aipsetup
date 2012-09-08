import os.path
import glob
import functools
import threading
import subprocess

from gi.repository import Gtk

import org.wayround.utils.text
import org.wayround.utils.gtk


import org.wayround.aipsetup.info
import org.wayround.aipsetup.config
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.version

NON_AUTOMATIC_NOT_SELECTED = "Non Automatic Not Selected"


class MainWindow:

    def __init__(self, config, no_loop):

        self.config = config
        self.currently_opened = None

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'latest_edit.glade'
            )

        ui = Gtk.Builder()
        ui.add_from_file(ui_file)

        self.ui = org.wayround.utils.gtk.widget_dict(ui)

        self.ui['window1'].connect("delete-event", Gtk.main_quit)
        self.ui['window1'].show_all()


        c = Gtk.TreeViewColumn("Non automatics")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)
        self.ui['treeview1'].append_column(c)

        c = Gtk.TreeViewColumn("Installation Packages")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)
        self.ui['treeview3'].append_column(c)

        c = Gtk.TreeViewColumn("Source Files")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)
        self.ui['treeview2'].append_column(c)


        self.ui['treeview1'].connect(
            'row-activated',
            self.onPackageListItemActivated
            )

        self.ui['treeview2'].connect(
            'row-activated',
            self.onSRCListItemActivated
            )

        self.ui['treeview3'].connect(
            'row-activated',
            self.onPKGListItemActivated
            )

        self.ui['button1'].connect(
            'clicked',
            self.onReloadListButtonActivated
            )

        self.ui['button2'].connect(
            'clicked',
            self.onSaveClicked
            )

        self.ui['button3'].connect(
            'clicked',
            self.onEditInfoClicked
            )

        self.ui['button4'].connect(
            'clicked',
            self.onNullLatestSourceClicked
            )

        self.ui['button5'].connect(
            'clicked',
            self.onNullLatestPackageClicked
            )

        self.load_package_list()
        self.load_item(None)

        return

    def load_package_list(self):

        db = org.wayround.aipsetup.pkgindex.PackageDatabase()

        names = db.get_list_of_non_automatic_package_info()

        names.sort(key=lambda i: i['name'])

        del db


        self.ui['treeview1'].set_model(None)
        lst = Gtk.ListStore(str)
        for i in names:
            lst.append([i['name']])

        self.ui['treeview1'].set_model(lst)

        if self.currently_opened:
            self.scroll_package_list_to_name(self.currently_opened)
        else:
            self.currently_opened = None
            self.load_item(None)

        return

    def scroll_package_list_to_name(self, name):
        org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
            self.ui['treeview1'],
            name
            )

        return

    def _load_item(self, name):

        if name == None:
            self.ui['entry1'].set_text(NON_AUTOMATIC_NOT_SELECTED)
            self.ui['entry2'].set_text(NON_AUTOMATIC_NOT_SELECTED)
            self.ui['entry1'].set_sensitive(False)
            self.ui['entry2'].set_sensitive(False)
            self.ui['button4'].set_sensitive(False)
            self.ui['entry1'].set_sensitive(False)
            self.ui['label7'].set_text(NON_AUTOMATIC_NOT_SELECTED)
            self.ui['treeview2'].set_sensitive(False)
            self.ui['button5'].set_sensitive(False)
            self.ui['entry2'].set_sensitive(False)
            self.ui['label8'].set_text(NON_AUTOMATIC_NOT_SELECTED)
            self.ui['treeview3'].set_sensitive(False)
        else:
            self.ui['window1'].set_sensitive(False)
            self.ui['spinner1'].start()
            db = org.wayround.aipsetup.pkgindex.PackageDatabase()

            info = db.package_info_record_to_dict(name)


            latest_source = db.get_latest_source(name)
            self.ui['entry1'].set_text(str(latest_source))
            if info['auto_newest_src']:
                self.ui['button4'].set_sensitive(False)
                self.ui['entry1'].set_sensitive(False)
                self.ui['label7'].set_text("Automatic")
                self.ui['treeview2'].set_sensitive(False)
            else:
                self.ui['button4'].set_sensitive(True)
                self.ui['entry1'].set_sensitive(True)
                self.ui['label7'].set_text("Select latest src file")
                self.ui['treeview2'].set_sensitive(True)



            latest_package = db.get_latest_package(name)
            self.ui['entry2'].set_text(str(latest_package))
            if info['auto_newest_pkg']:
                self.ui['button5'].set_sensitive(False)
                self.ui['entry2'].set_sensitive(False)
                self.ui['label8'].set_text("Automatic")
                self.ui['treeview3'].set_sensitive(False)
            else:
                self.ui['button5'].set_sensitive(True)
                self.ui['entry2'].set_sensitive(True)
                self.ui['label8'].set_text("Select latest src file")
                self.ui['treeview3'].set_sensitive(True)


            files = org.wayround.aipsetup.pkgindex.get_package_source_files(name, db)

            files.sort(
                reverse=True,
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.source_version_comparator
                    )
                )

            self.ui['treeview2'].set_model(None)
            lst = Gtk.ListStore(str)
            for i in files:
                lst.append([i])

            self.ui['treeview2'].set_model(lst)

            files = org.wayround.aipsetup.pkgindex.get_package_files(name, db)

            files.sort(
                reverse=True,
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

            self.ui['treeview3'].set_model(None)
            lst = Gtk.ListStore(str)
            for i in files:
                lst.append([i])

            self.ui['treeview3'].set_model(lst)

            del db

            org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
                self.ui['treeview2'],
                latest_source
                )

            org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
                self.ui['treeview3'],
                latest_package
                )

            self.currently_opened = name

            self.ui['spinner1'].stop()
            self.ui['window1'].set_sensitive(True)

        return 0


    def load_item(self, name):
        th = threading.Thread(target=self._load_item, args=(name,))
        th.start()
        th.join()

        return 0

    def wait(self):
        return Gtk.main()

    def close(self):
#        self.app.quit()
        return

    def onReloadListButtonActivated(self, button):
        self.load_package_list()

    def onPackageListItemActivated(self, view, path, column):

        sel = view.get_selection()

        model, iter = sel.get_selected()
        if not model == None and not iter == None:
            self.load_item(model[iter][0])

        return

    def onNullLatestSourceClicked(self, button):

        if self.currently_opened:
            db = org.wayround.aipsetup.pkgindex.PackageDatabase()
            db.set_latest_source(self.currently_opened, None, force=True)
            self.ui['entry1'].set_text(str(db.get_latest_source(self.currently_opened)))
            del db

        return

    def onNullLatestPackageClicked(self, button):

        if self.currently_opened:
            db = org.wayround.aipsetup.pkgindex.PackageDatabase()
            db.set_latest_package(self.currently_opened, None, force=True)
            self.ui['entry2'].set_text(str(db.get_latest_package(self.currently_opened)))
            del db

        return

    def onSRCListItemActivated(self, view, path, column):
        sel = view.get_selection()

        model, iter = sel.get_selected()
        if not model == None and not iter == None:
            self.ui['entry1'].set_text(model[iter][0])
        return

    def onPKGListItemActivated(self, view, path, column):
        sel = view.get_selection()

        model, iter = sel.get_selected()
        if not model == None and not iter == None:
            self.ui['entry2'].set_text(model[iter][0])
        return

    def onEditInfoClicked(self, button):

        if self.currently_opened:
            subprocess.Popen(
                [
                'aipsetup3',
                'info',
                'editor',
                self.currently_opened + '.xml'
                ]
                )

    def onSaveClicked(self, button):
        self.ui['spinner1'].start()

        if self.currently_opened:
            db = org.wayround.aipsetup.pkgindex.PackageDatabase()

            db.set_latest_source(self.currently_opened, self.ui['entry1'].get_text(), force=True)
            db.set_latest_package(self.currently_opened, self.ui['entry1'].get_text(), force=True)

            self.ui['entry1'].set_text(str(db.get_latest_source(self.currently_opened)))
            self.ui['entry2'].set_text(str(db.get_latest_package(self.currently_opened)))

            del db

            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Saved"
                )
            dia.run()
            dia.destroy()

        self.ui['spinner1'].stop()

        return

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


