
"""
Package tags editor
"""

import os.path

from gi.repository import Gtk

import org.wayround.utils.gtk

import org.wayround.aipsetup.config
import org.wayround.aipsetup.pkgindex


class MainWindow:

    def __init__(self, config):

        self.config = config
        self.currently_opened = None

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'tag_edit.glade'
            )

        ui = Gtk.Builder()
        ui.add_from_file(ui_file)

        self.ui = org.wayround.utils.gtk.widget_dict(ui)


        self.ui['window1'].connect("delete-event", Gtk.main_quit)
        self.ui['window1'].show_all()

        mode_selector = Gtk.ListStore(str)
        for i in ['Tag Vertized Mode', 'Package Vertized Mode']:
            mode_selector.append([i])

        r = Gtk.CellRendererText()
        self.ui['combobox1'].pack_start(r, True)
        self.ui['combobox1'].add_attribute(r, 'text', 0)

        self.ui['combobox1'].set_model(mode_selector)
        self.ui['combobox1'].set_active(0)
        self.edit_mode = 0

        self.ui['combobox1'].connect('changed', self.onModeComboBoxChanged)
#        c = Gtk.TreeViewColumn("File Names")
#        r = Gtk.CellRendererText()
#        c.pack_start(r, True)
#        c.add_attribute(r, 'text', 0)
#
#        self.ui['treeview1'].append_column(c)
#        self.ui['treeview1'].show_all()
#        self.ui['treeview1'].connect('row-activated', self.onPackageListItemActivated)
#
#        self.load_list()
#        self.load_buildscript_list()

        return


    def fill_left_treeview(self):

        if self.edit_mode == 0:
            pass

        return


    def wait(self):
        return Gtk.main()

    def close(self):
#        self.app.quit()
        return

    def onModeComboBoxChanged(self, object):

        self.edit_mode = self.ui['combobox1'].get_active()

        return

def main(mode=None, name=None):

    mw = MainWindow(org.wayround.aipsetup.config.config)

#    if isinstance(name_to_edit, str):
#        if mw.load_data(os.path.basename(name_to_edit)) != 0:
#            mw.close()
#        else:
#            if not no_loop:
#                mw.wait()
#    else:
#        if not no_loop:
#            mw.wait()

    mw.wait()

    return
