
"""
Edit package info on disk and update pkginfo database
"""

import copy
import glob
import logging
import os.path
import functools

from gi.repository import Gtk
from gi.repository import Gdk

import org.wayround.utils.gtk

import org.wayround.utils.path

import org.wayround.aipsetup.gtk
import org.wayround.aipsetup.info
import org.wayround.aipsetup.dbconnections
import org.wayround.aipsetup.controllers



class MainWindow:

    def __init__(self, config, info_ctl, tag_ctl, pkg_repo_ctl, src_repo_ctl):

        self.config = config
        self.info_ctl = info_ctl
        self.pkg_repo_ctl = pkg_repo_ctl
        self.src_repo_ctl = src_repo_ctl
        self.tag_ctl = tag_ctl

        self.currently_opened = None

        ui_file = os.path.join(
            os.path.dirname(__file__), 'ui', 'info_edit.glade'
            )

        ui = Gtk.Builder()
        ui.add_from_file(ui_file)

        self.ui = org.wayround.utils.gtk.widget_dict(ui)


#        self.ui['window1'].connect("delete-event", gtk_widget_hide_on_delete)
        self.ui['window1'].show_all()


        self.ui['window1'].connect('key-press-event', self.onWindow1KeyPressed)

        self.ui['button1'].connect('clicked', self.onListRealoadButtonActivated)

        self.ui['button2'].connect('clicked', self.onSaveAndUpdateButtonActivated)

        self.ui['button4'].connect('clicked', self.onShowAllSourceFilesButtonActivated)

        self.ui['button5'].connect('clicked', self.onShowFilteredSourceFilesButtonActivated)

        self.ui['button3'].connect('clicked', self.onQuitButtonClicked)


        c = Gtk.TreeViewColumn("File Names")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)

        self.ui['treeview1'].append_column(c)
        self.ui['treeview1'].show_all()
        self.ui['treeview1'].connect('row-activated', self.onPackageListItemActivated)

        r = Gtk.CellRendererText()
        self.ui['combobox1'].pack_start(r, True)
        self.ui['combobox1'].add_attribute(r, 'text', 0)


        self.load_list()
        self.load_buildscript_list()

        return


    def load_data(self, name):

        ret = 0

        filename = os.path.join(
            self.config['info_repo']['dir'],
            name
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
            data = org.wayround.aipsetup.info.read_info_file(filename)

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

                tag_db = self.tag_ctl.tag_db

                b = Gtk.TextBuffer()
                b.set_text('\n'.join(tag_db.get_tags(name[:-5])))
                self.ui['textview2'].set_buffer(b)

                b = Gtk.TextBuffer()
                b.set_text(data['filters'])
                self.ui['textview4'].set_buffer(b)

                m = self.ui['combobox1'].get_model()
                name_i = 0

                for i in range(len(m)):

                    if m[i][0] == str(data['buildscript']):
                        name_i = i
                        break

                self.ui['combobox1'].set_active(name_i)


                self.ui['entry2'].set_text(str(data['basename']))

                self.ui['entry3'].set_text(str(data['src_path_prefix']))

                self.ui['spinbutton1'].set_value(float(data['installation_priority']))

                self.ui['checkbutton2'].set_active(bool(data['removable']))

                self.ui['checkbutton1'].set_active(bool(data['reducible']))

                self.ui['checkbutton3'].set_active(bool(data['auto_newest_src']))

                self.ui['checkbutton4'].set_active(bool(data['auto_newest_pkg']))

                self.ui['checkbutton5'].set_active(bool(data['non_installable']))

                self.ui['checkbutton6'].set_active(bool(data['deprecated']))


                self.currently_opened = name
                self.ui['window1'].set_title(name + " - aipsetup v3 .json info file editor")

                self.scroll_package_list_to_name(name)

#        self.window.set_sensitive(True)

        return ret

    def save_data(self, name, update_db=False):

        ret = 0

        if not self.currently_opened:
            ret = 1
        else:
            filename = os.path.join(
                self.config['info_repo']['dir'],
                name
                )

            data = {}

            b = self.ui['textview1'].get_buffer()

            data['description'] = b.get_text(b.get_start_iter(), b.get_end_iter(), False)

            b = self.ui['textview4'].get_buffer()

            data['filters'] = b.get_text(b.get_start_iter(), b.get_end_iter(), False)

            data['home_page'] = self.ui['entry7'].get_text()

    #        b = self.ui['textview2'].get_buffer()
    #
    #        data['tags'] = org.wayround.utils.list.list_strip_remove_empty_remove_duplicated_lines(
    #            b.get_text(b.get_start_iter(), b.get_end_iter(), False).splitlines()
    #            )

    #        data['buildscript'] = self.ui['combobox-entry'].get_text()

            model = self.ui['combobox1'].get_model()
            active = self.ui['combobox1'].get_active()

            name = None
            if model:
                if active != -1:
                    name = model[active][0]

            data['buildscript'] = name

            data['basename'] = self.ui['entry2'].get_text()

            data['src_path_prefix'] = self.ui['entry3'].get_text()

            data['installation_priority'] = int(self.ui['spinbutton1'].get_value())

            data['removable'] = self.ui['checkbutton2'].get_active()

            data['reducible'] = self.ui['checkbutton1'].get_active()

            data['auto_newest_src'] = self.ui['checkbutton3'].get_active()

            data['auto_newest_pkg'] = self.ui['checkbutton4'].get_active()

            data['non_installable'] = self.ui['checkbutton5'].get_active()

            data['deprecated'] = self.ui['checkbutton6'].get_active()

            if org.wayround.aipsetup.info.write_info_file(filename, data) != 0:
                dia = Gtk.MessageDialog(
                    self.ui['window1'],
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't save to file {}".format(filename)
                    )
                dia.run()
                dia.destroy()
                ret = 1
            else:

                dbu = ''
                if update_db:
                    try:
                        self.info_ctl.load_info_records_from_fs(
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

        mask = os.path.join(self.config['info_repo']['dir'], '*.json')

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

        files = glob.glob(
            org.wayround.utils.path.join(
                self.config['builder_repo']['building_scripts_dir'], '*.py'
                )
            )

        files.sort()

        model = self.ui['combobox1'].get_model()
        active = self.ui['combobox1'].get_active()

        name = None
        if model:
            if active != -1:
                name = model[active][0]


        self.ui['combobox1'].set_model(None)

        lst = Gtk.ListStore(str)
        lst.append('')
        for i in files:
            lst.append([os.path.basename(i)[:-3]])

        self.ui['combobox1'].set_model(lst)
        model = self.ui['combobox1'].get_model()

        name_i = -1
        if model:
            for i in range(len(model)):
                if model[i][0] == name:
                    name_i = i
                    break

        self.ui['combobox1'].set_active(name_i)

        return

    def scroll_package_list_to_name(self, name):
        org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
            self.ui['treeview1'],
            name
            )
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

    def onWindow1KeyPressed(self, widget, event):
#        print("keyval ==     {}".format(repr(hex(event.keyval))))
#        print("state  ==     {}".format(repr(bin(event.state))))
#
#        print("CONTROL_MASK: {}".format(repr(bin(event.state & Gdk.ModifierType.CONTROL_MASK))))
#        print("SHIFT_MASK:   {}".format(repr(bin(event.state & Gdk.ModifierType.SHIFT_MASK))))
#        print("MOD1_MASK:    {}".format(repr(bin(event.state & Gdk.ModifierType.MOD1_MASK))))
#        print("")

        if (
            (event.keyval == Gdk.KEY_q)
            and
            (event.state & Gdk.ModifierType.CONTROL_MASK != 0)
            ):
            org.wayround.aipsetup.gtk.stop_session()

        if (
            (event.keyval == Gdk.KEY_s)
            and
            (event.state & Gdk.ModifierType.CONTROL_MASK != 0)
            ):
            self.onSaveAndUpdateButtonActivated(None)

        if (
            ((event.keyval == Gdk.KEY_F5))
            or
            (
             (event.keyval == Gdk.KEY_r)
             and
             (event.state & Gdk.ModifierType.CONTROL_MASK != 0)
             )
            ):
            self.onListRealoadButtonActivated(None)

    def onSaveAndUpdateButtonActivated(self, button):
        if self.ui['entry1'].get_text() == '':
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
            self.save_data(self.currently_opened, update_db=True)

    def onShowAllSourceFilesButtonActivated(self, button):

        if self.ui['entry1'].get_text() == '':
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
            lst = self.src_repo_ctl.get_package_source_files(
                self.ui['entry1'].get_text()[:-5],
                info_ctl=self.info_ctl,
                filtered=False
                )

            logging.debug("get_package_source_files returned {}".format(lst))

            if not isinstance(lst, list):
                dia = Gtk.MessageDialog(
                    self.ui['window1'],
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting source files from database"
                    )
                dia.run()
                dia.destroy()
            else:
                org.wayround.utils.gtk.text_view(
                    '\n'.join(lst),
                    "{} - Non-filtered tarballs".format(self.ui['entry1'].get_text()[:-5])
                    )

    def onQuitButtonClicked(self, button):
        org.wayround.aipsetup.gtk.stop_session()

    def onShowFilteredSourceFilesButtonActivated(self, button):

        if self.ui['entry1'].get_text() == '':
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
            lst = self.src_repo_ctl.get_package_source_files(
                self.ui['entry1'].get_text()[:-5],
                info_ctl=self.info_ctl,
                filtered=True
                )

            lst.sort(
                key=functools.cmp_to_key(
                    org.wayround.utils.version.source_version_comparator
                    ),
                reverse=True
                )

            logging.debug("get_package_source_files returned {}".format(lst))

            if not isinstance(lst, list):
                dia = Gtk.MessageDialog(
                    self.ui['window1'],
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting source files from database"
                    )
                dia.run()
                dia.destroy()
            else:
                org.wayround.utils.gtk.text_view(
                    '\n'.join(lst),
                    "{} - Filtered tarballs".format(self.ui['entry1'].get_text()[:-5])
                    )



    def onListRealoadButtonActivated(self, button):
        self.load_buildscript_list()
        self.load_list()

    def onPackageListItemActivated(self, view, path, column):

        sel = view.get_selection()

        model, iter = sel.get_selected()
        if not model == None and not iter == None:
            self.load_data(model[iter][0])

        return


def main(name_to_edit=None, config=None):

    # TODO: re do to *_new

    info_ctl = org.wayround.aipsetup.controllers.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.controllers.pkg_repo_ctl(config)

    src_repo_ctl = org.wayround.aipsetup.controllers.src_repo_ctl(config)

    tag_ctl = org.wayround.aipsetup.controllers.tag_ctl(config)

    mw = MainWindow(config, info_ctl, tag_ctl, pkg_repo_ctl, src_repo_ctl)

    if isinstance(name_to_edit, str):
        if mw.load_data(os.path.basename(name_to_edit)) == 0:
            org.wayround.aipsetup.gtk.start_session()
    else:
        org.wayround.aipsetup.gtk.start_session()

    return
