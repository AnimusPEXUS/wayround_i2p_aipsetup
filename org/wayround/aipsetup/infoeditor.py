import os.path
import glob
import subprocess
import logging

#import PyQt4.uic
#import PyQt4.QtGui

import org.wayround.utils.text

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config
import org.wayround.aipsetup.pkgindex

from gi.repository import Gtk

class MainWindow:

    def __init__(self, config, no_loop):

        self.config = config
        self.currently_opened = ''

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'info_edit.glade'
            )

        self.ui = Gtk.Builder()
        self.ui.add_from_file(ui_file)


        self.window = self.ui.get_object('window1')
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()


        refreshListButton = self.ui.get_object('button5')
        refreshListButton.connect('clicked', self.onListRealoadButtonActivated)

        refreshListButton = self.ui.get_object('button3')
        refreshListButton.connect('clicked', self.onRevertButtonActivated)

        refreshListButton = self.ui.get_object('button4')
        refreshListButton.connect('clicked', self.onSaveButtonActivated)

        refreshListButton = self.ui.get_object('button2')
        refreshListButton.connect('clicked', self.onSaveAndUpdateButtonActivated)

        refreshListButton = self.ui.get_object('button1')
        refreshListButton.connect('clicked', self.onEditLatestButtonActivated)



        c = Gtk.TreeViewColumn("File Names")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)

        treeview1 = self.ui.get_object('treeview1')
        treeview1.append_column(c)
        treeview1.show_all()
        treeview1.connect('row-activated', self.onListItemActivated)

        self.window.show()
        self.load_list()


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
                self.window,
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
                    self.window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't read data from file"
                    )
                dia.run()
                dia.destroy()
                ret = 1
            else:

                self.scroll_to_name(name)

                e = self.ui.get_object('entry1')
                e.set_text(name)

                b = Gtk.TextBuffer()
                b.set_text(data['description'])

                e = self.ui.get_object('textview1')
                e.set_buffer(b)

                e = self.ui.get_object('entry7')
                e.set_text(data['home_page'])

                b = Gtk.TextBuffer()
                b.set_text('\n'.join(data['tags']))

                e = self.ui.get_object('textview2')
                e.set_buffer(b)

                e = self.ui.get_object('entry5')
                e.set_text(data['buildinfo'])

                e = self.ui.get_object('entry2')
                e.set_text(data['basename'])


                e = self.ui.get_object('entry3')
                e.set_text(data['version_re'])

                e = self.ui.get_object('spinbutton1')
                e.set_value(float(data['installation_priority']))

                e = self.ui.get_object('checkbutton2')
                e.set_active(bool(data['deletable']))

                e = self.ui.get_object('checkbutton1')
                e.set_active(bool(data['updatable']))

                e = self.ui.get_object('checkbutton3')
                e.set_active(bool(data['auto_newest_src']))

                e = self.ui.get_object('checkbutton4')
                e.set_active(bool(data['auto_newest_pkg']))

                e = self.ui.get_object('button1')
                e.set_sensitive(
                    (
                        not self.ui.get_object('checkbutton3').get_active()
                        or
                        not self.ui.get_object('checkbutton4').get_active()
                        )
                    )

                db = org.wayround.aipsetup.pkgindex.PackageDatabase()

                e = self.ui.get_object('entry4')
                e.set_text(str(db.get_latest_source(name[:-4])))

                e = self.ui.get_object('entry6')
                e.set_text(str(db.get_latest_package(name[:-4])))

                del db

                self.currently_opened = name
                self.window.set_title(name + " - aipsetup v3 .xml info file editor")

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

        e = self.ui.get_object('textview1')
        b = e.get_buffer()

        data['description'] = b.get_text(b.get_start_iter(), b.get_end_iter(), False)

        e = self.ui.get_object('entry7')
        data['home_page'] = e.get_text()


        e = self.ui.get_object('textview2')
        b = e.get_buffer()

        b = Gtk.TextBuffer()
        data['tags'] = org.wayround.utils.text.strip_remove_empty_remove_duplicated_lines(
            str(b.get_text(b.get_start_iter(), b.get_end_iter(), False).splitlines())
            )

        e = self.ui.get_object('entry5')
        data['buildinfo'] = e.get_text()

        e = self.ui.get_object('entry2')
        data['basename'] = e.get_text()

        e = self.ui.get_object('entry3')
        data['version_re'] = e.get_text()

        e = self.ui.get_object('spinbutton1')
        data['installation_priority'] = int(e.get_value())

        e = self.ui.get_object('checkbutton2')
        data['deletable'] = e.get_active()

        e = self.ui.get_object('checkbutton1')
        data['updatable'] = e.get_active()

        e = self.ui.get_object('checkbutton3')
        data['auto_newest_src'] = e.get_active()

        e = self.ui.get_object('checkbutton4')
        data['auto_newest_pkg'] = e.get_active()


        if org.wayround.aipsetup.info.write_to_file(filename, data) != 0:
            dia = Gtk.MessageDialog(
                self.window,
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
                    db = org.wayround.aipsetup.pkgindex.PackageDatabase()
                    db.load_package_info_from_filesystem(
                        [filename], rewrite_existing=True
                        )
                    del db
                    dbu = "DB updated"
                except:
                    dbu = "Some error while updating DB"
                    logging.exception(dbu)

            if dbu != '':
                dbu = '\n' + dbu

            dia = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                'File saved' + dbu
                )
            dia.run()
            dia.destroy()

        return ret

    def onRevertButtonActivated(self, button):
        if self.load_data(self.currently_opened) != 0:
            dia = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't reread file"
                )
            dia.run()
            dia.destroy()
        else:
            dia = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Rereaded data from file"
                )
            dia.run()
            dia.destroy()

        return

    def onSaveButtonActivated(self, button):
        self.save_data(self.currently_opened)

    def onSaveAndUpdateButtonActivated(self, toggle):
        self.save_data(self.currently_opened, update_db=True)

    def onListRealoadButtonActivated(self, button):
        self.load_list()

    def onListItemActivated(self, view, path, column):

        sel = view.get_selection()

        model, iter = sel.get_selected()
        if not model == None and not iter == None:
            self.load_data(model[iter][0])

        return

    def onEditLatestButtonActivated(self, toggle):

        e = self.ui.get_object('entry1')
        if e.get_text().endswith('.xml'):
            subprocess.Popen(
                [
                'aipsetup3',
                'pkgindex',
                'edit_latests',
                e.get_text()[:-4]
                ]
                )

    def load_list(self):

        mask = os.path.join(self.config['info'], '*.xml')

        files = glob.glob(mask)

        files.sort()

        treeview = self.ui.get_object('treeview1')
        treeview.set_model(None)

        lst = Gtk.ListStore(str)
        for i in files:
            base = os.path.basename(i)
            lst.append([base])

        treeview.set_model(lst)
        if self.currently_opened:
            self.scroll_to_name(self.currently_opened)
        return

    def scroll_to_name(self, name):
        e = self.ui.get_object('treeview1')
        sel = e.get_selection()
        model = e.get_model()
        ind = -1
        if model:
            for i in model:
                ind += 1
                if i[0] == name:
                    path = Gtk.TreePath.new_from_string(str(ind))
                    sel.select_path(path)
                    e.scroll_to_cell(path, None, True, 0.5, 0.5)
                    break

        return

    def wait(self):
        return Gtk.main()

    def close(self):
#        self.app.quit()
        return

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
