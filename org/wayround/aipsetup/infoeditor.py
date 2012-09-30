import os.path
import glob
import subprocess
import logging

from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config

import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkglatest
import org.wayround.aipsetup.pkgtag


class MainWindow:

    def __init__(self, config, no_loop):

        self.config = config
        self.currently_opened = None

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'info_edit.glade'
            )

        ui = Gtk.Builder()
        ui.add_from_file(ui_file)

        self.ui = org.wayround.utils.gtk.widget_dict(ui)


        self.ui['window1'].connect("delete-event", Gtk.main_quit)
        self.ui['window1'].show_all()


        self.ui['button5'].connect('clicked', self.onListRealoadButtonActivated)

        self.ui['button2'].connect('clicked', self.onSaveAndUpdateButtonActivated)

        self.ui['button1'].connect('clicked', self.onEditLatestButtonActivated)

        self.ui['button6'].connect('clicked', self.onReloadComboActivated)



        c = Gtk.TreeViewColumn("File Names")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)

        self.ui['treeview1'].append_column(c)
        self.ui['treeview1'].show_all()
        self.ui['treeview1'].connect('row-activated', self.onPackageListItemActivated)

        self.load_list()
        self.load_buildscript_list()

        return


    def load_data(self, name):

        ret = 0

        filename = os.path.join(
            self.config['info'],
            '%(name)s' % {
                'name': name
                }
            )

        if not os.path.isfile(filename):
            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "File not exists"
                )
            dia.run()
            dia.destroy()

        else:
            data = org.wayround.aipsetup.info.read_from_file(filename)

            if not isinstance(data, dict):
                dia = Gtk.MessageDialog(
                    self.ui['window1'],
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't read data from file"
                    )
                dia.run()
                dia.destroy()
                ret = 1
            else:

                self.ui['entry1'].set_text(name)

                b = Gtk.TextBuffer()
                b.set_text(str(data['description']))

                self.ui['textview1'].set_buffer(b)

                self.ui['entry7'].set_text(str(data['home_page']))

                tag_db = org.wayround.aipsetup.pkgtag.package_tags_connection()

                b = Gtk.TextBuffer()
                b.set_text('\n'.join(tag_db.get_tags(name[:-4])))

                self.ui['textview2'].set_buffer(b)

                self.ui['combobox-entry'].set_text(str(data['buildscript']))

                self.ui['entry2'].set_text(str(data['basename']))

                self.ui['entry3'].set_text(str(data['version_re']))

                self.ui['spinbutton1'].set_value(float(data['installation_priority']))

                self.ui['checkbutton2'].set_active(bool(data['removable']))

                self.ui['checkbutton1'].set_active(bool(data['reducible']))

                self.ui['checkbutton3'].set_active(bool(data['auto_newest_src']))

                self.ui['checkbutton4'].set_active(bool(data['auto_newest_pkg']))

                self.ui['button1'].set_sensitive(
                    (
                        not self.ui['checkbutton3'].get_active()
                        or
                        not self.ui['checkbutton4'].get_active()
                        )
                    )

                self.ui['entry4'].set_text(
                    str(
                        org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(
                            name[:-4]
                            )
                        )
                    )

                self.ui['entry6'].set_text(
                    str(
                        org.wayround.aipsetup.pkglatest.get_latest_src_from_record(
                            name[:-4]
                            )
                        )
                    )

                self.currently_opened = name
                self.ui['window1'].set_title(name + " - aipsetup v3 .json info file editor")

                self.scroll_package_list_to_name(name)

#        self.window.set_sensitive(True)

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

        b = self.ui['textview1'].get_buffer()

        data['description'] = b.get_text(b.get_start_iter(), b.get_end_iter(), False)

        data['home_page'] = self.ui['entry7'].get_text()

#        b = self.ui['textview2'].get_buffer()
#
#        data['tags'] = org.wayround.utils.list.list_strip_remove_empty_remove_duplicated_lines(
#            b.get_text(b.get_start_iter(), b.get_end_iter(), False).splitlines()
#            )

        data['buildscript'] = self.ui['combobox-entry'].get_text()

        data['basename'] = self.ui['entry2'].get_text()

        data['version_re'] = self.ui['entry3'].get_text()

        data['installation_priority'] = int(self.ui['spinbutton1'].get_value())

        data['removable'] = self.ui['checkbutton2'].get_active()

        data['reducible'] = self.ui['checkbutton1'].get_active()

        data['auto_newest_src'] = self.ui['checkbutton3'].get_active()

        data['auto_newest_pkg'] = self.ui['checkbutton4'].get_active()


        if org.wayround.aipsetup.info.write_to_file(filename, data) != 0:
            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't save to file %(name)s" % {
                    'name': filename
                    }
                )
            dia.run()
            dia.destroy()
            ret = 1
        else:

            dbu = ''
            if update_db:
                try:
                    org.wayround.aipsetup.pkginfo.load_info_records_from_fs(
                        [filename], rewrite_existing=True
                        )

                    dbu = "DB updated"
                except:
                    dbu = "Some error while updating DB"
                    logging.exception(dbu)

            if dbu != '':
                dbu = '\n' + dbu

            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                'File saved' + dbu
                )
            dia.run()
            dia.destroy()

        return ret


    def load_list(self):

        mask = os.path.join(self.config['info'], '*.json')

        files = glob.glob(mask)

        files.sort()

        self.ui['treeview1'].set_model(None)

        lst = Gtk.ListStore(str)
        for i in files:
            base = os.path.basename(i)
            lst.append([base])

        self.ui['treeview1'].set_model(lst)
        if self.currently_opened:
            self.scroll_package_list_to_name(self.currently_opened)
        return

    def load_buildscript_list(self):

        files = glob.glob(self.config['buildscript'] + os.path.sep + '*.py')

        files.sort()

        self.ui['combobox1'].set_model(None)

        lst = Gtk.ListStore(str)
        for i in files:
            lst.append([os.path.basename(i)[:-3]])

        self.ui['combobox1'].set_model(lst)
        self.ui['combobox1'].set_entry_text_column(0)


    def scroll_package_list_to_name(self, name):
        org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
            self.ui['treeview1'],
            name
            )
        return

    def wait(self):
        return Gtk.main()

    def close(self):
#        self.app.quit()
        return

    def onRevertButtonActivated(self, button):
        if self.load_data(self.currently_opened) != 0:
            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't reread file"
                )
            dia.run()
            dia.destroy()
        else:
            dia = Gtk.MessageDialog(
                self.ui['window1'],
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Rereaded data from file"
                )
            dia.run()
            dia.destroy()

        return

    def onReloadComboActivated(self, buton):
        self.load_buildscript_list()

    def onSaveAndUpdateButtonActivated(self, toggle):
        self.save_data(self.currently_opened, update_db=True)

    def onListRealoadButtonActivated(self, button):
        self.load_list()

    def onPackageListItemActivated(self, view, path, column):

        sel = view.get_selection()

        model, iter = sel.get_selected()
        if not model == None and not iter == None:
            self.load_data(model[iter][0])

        return

    def onEditLatestButtonActivated(self, toggle):

        if self.ui['entry1'].get_text().endswith('.json'):
            subprocess.Popen(
                [
                'aipsetup3',
                'repo',
                'latests',
                self.ui['entry1'].get_text()[:-4]
                ]
                )

def main(name_to_edit=None, no_loop=False):
#    s = Gtk.Settings.get_default()
#    s.set_string_property("gtk-theme-name", "Adwaita", "")
#    s.set_long_property("gtk-xft-dpi", 75000, "")
#    Gtk.Settings.set_string_property("gtk-theme-name", "Default", "")
    mw = MainWindow(org.wayround.aipsetup.config.config, no_loop)

    if isinstance(name_to_edit, str):
        if mw.load_data(os.path.basename(name_to_edit)) != 0:
            mw.close()
        else:
            if not no_loop:
                mw.wait()
    else:
        if not no_loop:
            mw.wait()

    return
