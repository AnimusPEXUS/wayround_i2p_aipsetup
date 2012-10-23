import os.path
import functools
import subprocess


from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.aipsetup.version

import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkglatest


NON_AUTOMATIC_NOT_SELECTED = "Package Not Selected"


class MainWindow:

    def __init__(self):

        self.currently_opened = None

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'latest_edit.glade'
            )

        ui = Gtk.Builder()
        ui.add_from_file(ui_file)

        self.ui = org.wayround.utils.gtk.widget_dict(ui)

#        self.ui['window1'].connect("delete-event", gtk_widget_hide_on_delete)
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

        names = org.wayround.aipsetup.pkginfo.get_non_automatic_packages_info_list()

        names.sort(key=lambda i: i['name'])

        self.ui['treeview1'].set_model(None)
        lst = Gtk.ListStore(str)
        for i in names:
            lst.append([i['name']])

        self.ui['treeview1'].set_model(lst)

        if self.currently_opened:
            org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
                self.ui['treeview1'],
                self.currently_opened
                )

        else:
            self.currently_opened = None
            self.load_item(None)

        return


    def load_item(self, name):
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
            self.currently_opened = None
        else:
            self.ui['window1'].set_sensitive(False)

            info = org.wayround.aipsetup.pkginfo.get_package_info_record(
                name
                )

            if not isinstance(info, dict):
                dia = Gtk.MessageDialog(
                    self.ui['window1'],
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting information from DB\n"
                    "Perhaps `aipsetup repo load' required"
                    )
                dia.run()
                dia.destroy()

            else:

                latest_source = org.wayround.aipsetup.pkglatest.get_latest_src_from_record(
                    name
                    )

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



                latest_package = org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(
                    name
                    )

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

                sources_error = False
                packages_error = False

                self.ui['treeview2'].set_model(None)
                self.ui['treeview3'].set_model(None)

                files = org.wayround.aipsetup.pkgindex.get_package_source_files(
                    name
                    )

                if not isinstance(files, list):
                    sources_error = True
                else:

                    files.sort(
                        reverse=True,
                        key=functools.cmp_to_key(
                            org.wayround.aipsetup.version.source_version_comparator
                            )
                        )

                    lst = Gtk.ListStore(str)
                    for i in files:
                        lst.append([i])

                    self.ui['treeview2'].set_model(lst)

                    org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
                        self.ui['treeview2'],
                        latest_source
                        )

                files = org.wayround.aipsetup.pkgindex.get_package_files(
                    name
                    )

                if not isinstance(files, list):
                    packages_error = True
                else:

                    files.sort(
                        reverse=True,
                        key=functools.cmp_to_key(
                            org.wayround.aipsetup.version.package_version_comparator
                            )
                        )

                    lst = Gtk.ListStore(str)
                    for i in files:
                        lst.append([i])

                    self.ui['treeview3'].set_model(lst)

                    org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
                        self.ui['treeview3'],
                        latest_package
                        )

                if packages_error or sources_error:

                    error_text = ''

                    if packages_error:
                        error_text += 'Error getting package files list\n'

                    if sources_error:
                        error_text += 'Error getting source files list\n'

                    error_text += 'Check package repository registration'

                    dia = Gtk.MessageDialog(
                        self.ui['window1'],
                        Gtk.DialogFlags.MODAL,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        error_text
                        )
                    dia.run()
                    dia.destroy()

                self.currently_opened = name
                self.scrollPackageListToItem(name)
                self.ui['window1'].set_title(str(name) + " - Latest Files Editor")

                self.ui['window1'].set_sensitive(True)

        return 0

    def scrollPackageListToItem(self, name):
        org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
            self.ui['treeview1'],
            name
            )

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
            org.wayround.aipsetup.pkglatest.set_latest_src_to_record(
                self.currently_opened,
                None,
                force=True
                )

            latest_db = org.wayround.aipsetup.dbconnections.latest_db()
            latest_db.commit()

            self.ui['entry1'].set_text(
                str(
                    org.wayround.aipsetup.pkglatest.get_latest_src_from_record(
                        self.currently_opened
                        )
                    )
                )

        return

    def onNullLatestPackageClicked(self, button):

        if self.currently_opened:
            org.wayround.aipsetup.pkglatest.set_latest_pkg_to_record(
                self.currently_opened,
                None,
                force=True
                )
            self.ui['entry2'].set_text(
                str(
                    org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(
                        self.currently_opened
                        )
                    )
                )

            latest_db = org.wayround.aipsetup.dbconnections.latest_db()
            latest_db.commit()

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

        import org.wayround.aipsetup.infoeditor

        if not self.currently_opened:
            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Record not selected\n\n(hint: double click on list item to select one)"
                )
            dia.run()
            dia.destroy()
        else:
            org.wayround.aipsetup.infoeditor.main(
                self.currently_opened + '.json'
                )

    def onSaveClicked(self, button):

        if not self.currently_opened:

            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Record not selected\n\n(hint: double click on list item to select one)"
                )
            dia.run()
            dia.destroy()

        else:
            org.wayround.aipsetup.pkglatest.set_latest_src_to_record(
                self.currently_opened,
                self.ui['entry1'].get_text(),
                force=True
                )
            org.wayround.aipsetup.pkglatest.set_latest_pkg_to_record(
                self.currently_opened,
                self.ui['entry2'].get_text(),
                force=True
                )

            self.ui['entry1'].set_text(
                str(
                    org.wayround.aipsetup.pkglatest.get_latest_src_from_record(
                        self.currently_opened
                        )
                    )
                )
            self.ui['entry2'].set_text(
                str(
                    org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(
                        self.currently_opened
                        )
                    )
                )

            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Saved"
                )
            dia.run()
            dia.destroy()

            latest_db = org.wayround.aipsetup.dbconnections.latest_db()
            latest_db.commit()

        return

def main(name_to_edit=None):

    mw = MainWindow()

    if isinstance(name_to_edit, str):
        if mw.load_item(name_to_edit) != 0:
            org.wayround.aipsetup.gtk.start_session()
    else:
        org.wayround.aipsetup.gtk.start_session()

    return


