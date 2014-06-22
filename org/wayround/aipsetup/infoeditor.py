
"""
Edit package info on disk and update pkginfo database
"""

import collections
import functools
import glob
import logging
import os.path

from gi.repository import Gdk, Gtk

import org.wayround.aipsetup.controllers
import org.wayround.aipsetup.gtk
import org.wayround.aipsetup.gui.infoeditor
import org.wayround.aipsetup.info
import org.wayround.utils.gtk
import org.wayround.utils.list


class MainWindow:

    def __init__(
        self, info_ctl, tag_ctl, src_client, pkg_client,
        acceptable_source_name_extensions
        ):

#        self.config = config
        self.info_ctl = info_ctl
#        self.src_repo_ctl = src_repo_ctl
        self.src_client = src_client
        self.pkg_client = pkg_client
        self.tag_ctl = tag_ctl
        self.acceptable_source_name_extensions = (
            acceptable_source_name_extensions
            )

        self.currently_opened = None

        self.ui = org.wayround.aipsetup.gui.infoeditor.InfoEditorUi()

        self.ui.window.show_all()

        self.ui.window.connect(
            'key-press-event',
            self.onWindow1KeyPressed
            )

        self.ui.refresh_list_button.connect(
            'clicked',
            self.onListRealoadButtonActivated
            )

        self.ui.save_button.connect(
            'clicked',
            self.onSaveAndUpdateButtonActivated
            )

        self.ui.show_not_filtered_button.connect(
            'clicked',
            self.onShowAllSourceFilesButtonActivated
            )

        self.ui.show_filtered_button.connect(
            'clicked',
            self.onShowFilteredSourceFilesButtonActivated
            )

        self.ui.quit_button.connect('clicked', self.onQuitButtonClicked)

        self.ui.tree_view1.show_all()
        self.ui.tree_view1.connect(
            'row-activated',
            self.onPackageListItemActivated
            )

        self.load_list()

        return

    def load_data(self, filename):

        ret = 0

        filename = os.path.join(
            self.info_ctl.get_info_dir(),
            filename
            )

        if not os.path.isfile(filename):
            dia = Gtk.MessageDialog(
                self.ui.window,
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
                    self.ui.window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Can't read data from file"
                    )
                dia.run()
                dia.destroy()
                ret = 1
            else:

                name = os.path.basename(filename)[:-5]

                self.ui.name_entry.set_text(name)

                b = Gtk.TextBuffer()
                b.set_text(str(data['description']))

                self.ui.description_tw.set_buffer(b)

                self.ui.homepage_entry.set_text(str(data['home_page']))

                tag_db = self.tag_ctl.tag_db

                b = Gtk.TextBuffer()
                b.set_text('\n'.join(tag_db.get_tags(name)))
                self.ui.tags_tw.set_buffer(b)

                b = self.ui.filters_tw.get_buffer()
                b.set_text(data['filters'])

                self.ui.basename_entry.set_text(str(data['basename']))

                self.ui.buildscript_entry.set_text(str(data['buildscript']))

                self.ui.install_priority_scale.set_value(
                    float(data['installation_priority'])
                    )

                self.ui.removable_cb.set_active(bool(data['removable']))

                self.ui.reducible_cb.set_active(bool(data['reducible']))

                self.ui.non_installable_cb.set_active(
                    bool(data['non_installable'])
                    )

                self.ui.deprecated_cb.set_active(bool(data['deprecated']))

                self.currently_opened = filename
                self.ui.window.set_title(
                    filename + " - aipsetup v3 .json info file editor"
                    )

                self.scroll_package_list_to_name(os.path.basename(filename))

#        self.window.set_sensitive(True)

        return ret

    def save_data(self, filename, update_db=False):

        ret = 0

        if not self.currently_opened:
            ret = 1
        else:
            filename = os.path.join(
                self.info_ctl.get_info_dir(),
                filename
                )

            name = os.path.basename(filename)[:-5]

            data = {}

            b = self.ui.description_tw.get_buffer()

            data['description'] = \
                b.get_text(b.get_start_iter(), b.get_end_iter(), False)

            b = self.ui.filters_tw.get_buffer()
            data['filters'] = \
                b.get_text(b.get_start_iter(), b.get_end_iter(), False)

            b = self.ui.tags_tw.get_buffer()
            tags = \
                b.get_text(b.get_start_iter(), b.get_end_iter(), False)

            tags = \
                org.wayround.utils.list.\
                    list_strip_remove_empty_remove_duplicated_lines(
                        tags
                        )

            tag_db = self.tag_ctl.tag_db

            tag_db.set_tags(name, tags)

            self.tag_ctl.save_tags_to_fs()

            data['home_page'] = self.ui.homepage_entry.get_text()

            data['buildscript'] = self.ui.buildscript_entry.get_text()

            data['basename'] = self.ui.basename_entry.get_text()

            data['installation_priority'] = \
                int(self.ui.install_priority_scale.get_value())

            data['removable'] = self.ui.removable_cb.get_active()

            data['reducible'] = self.ui.reducible_cb.get_active()

            data['non_installable'] = self.ui.non_installable_cb.get_active()

            data['deprecated'] = self.ui.deprecated_cb.get_active()

            data_o = collections.OrderedDict()

            keys = \
                org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys()

            for i in keys:
                data_o[i] = data[i]

            data_o['name'] = name

            data = data_o

            if org.wayround.aipsetup.info.write_info_file(filename, data) != 0:
                dia = Gtk.MessageDialog(
                    self.ui.window,
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
                    self.ui.window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    'File saved' + dbu
                    )
                dia.run()
                dia.destroy()

        return ret

    def load_list(self):

        mask = os.path.join(self.info_ctl.get_info_dir(), '*.json')

        files = glob.glob(mask)

        files.sort()

        self.ui.tree_view1.set_model(None)

        lst = Gtk.ListStore(str)
        for i in files:
            base = os.path.basename(i)
            lst.append([base])

        self.ui.tree_view1.set_model(lst)
        if self.currently_opened:
            self.scroll_package_list_to_name(
                os.path.basename(self.currently_opened)
                )
        return

    def scroll_package_list_to_name(self, name):
        org.wayround.utils.gtk.list_view_select_and_scroll_to_name(
            self.ui.tree_view1,
            name
            )
        return

    def onRevertButtonActivated(self, button):
        if self.load_data(self.currently_opened) != 0:
            dia = Gtk.MessageDialog(
                self.ui.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Can't reread file"
                )
            dia.run()
            dia.destroy()
        else:
            dia = Gtk.MessageDialog(
                self.ui.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Rereaded data from file"
                )
            dia.run()
            dia.destroy()

        return

    def onWindow1KeyPressed(self, widget, event):

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
        if self.ui.name_entry.get_text() == '':
            dia = Gtk.MessageDialog(
                self.ui.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Record not selected\n\n"
                "(hint: double click on list item to select one)"
                )
            dia.run()
            dia.destroy()
        else:
            self.save_data(self.currently_opened, update_db=True)

    def onShowAllSourceFilesButtonActivated(self, button):

        if self.ui.name_entry.get_text() == '':
            dia = Gtk.MessageDialog(
                self.ui.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Record not selected\n\n"
                "(hint: double click on list item to select one)"
                )
            dia.run()
            dia.destroy()
        else:
            lst = self.src_client.files(
                self.ui.basename_entry.get_text()
                )

            logging.debug("get_package_source_files returned {}".format(lst))

            if not isinstance(lst, list):
                dia = Gtk.MessageDialog(
                    self.ui.window,
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
                    "{} - Non-filtered tarballs".format(
                        self.ui.name_entry.get_text()
                        )
                    )

    def onQuitButtonClicked(self, button):
        org.wayround.aipsetup.gtk.stop_session()

    def onShowFilteredSourceFilesButtonActivated(self, button):

        if self.ui.name_entry.get_text() == '':
            dia = Gtk.MessageDialog(
                self.ui.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Record not selected\n\n"
                "(hint: double click on list item to select one)"
                )
            dia.run()
            dia.destroy()
        else:
            lst = self.pkg_client.tarballs(self.ui.name_entry.get_text())

            def source_version_comparator(v1, v2):
                return org.wayround.utils.version.source_version_comparator(
                    v1, v2,
                    self.acceptable_source_name_extensions
                    )

            logging.debug("get_package_source_files returned {}".format(lst))

            if not isinstance(lst, list):
                dia = Gtk.MessageDialog(
                    self.ui.window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Error getting source files from database"
                    )
                dia.run()
                dia.destroy()
            else:
                lst.sort(
                    key=functools.cmp_to_key(
                        source_version_comparator
                        ),
                    reverse=True
                    )

                org.wayround.utils.gtk.text_view(
                    '\n'.join(lst),
                    "{} - Filtered tarballs".format(
                        self.ui.name_entry.get_text()
                        )
                    )

        return

    def onListRealoadButtonActivated(self, button):
        self.load_list()

    def onPackageListItemActivated(self, view, path, column):

        sel = view.get_selection()

        model, itera = sel.get_selected()
        if not model == None and not itera == None:
            self.load_data(model[itera][0])

        return


def main(name_to_edit=None, config=None):

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    src_client = org.wayround.aipsetup.controllers.src_client_by_config(config)

    pkg_client = org.wayround.aipsetup.controllers.pkg_client_by_config(config)

    tag_ctl = org.wayround.aipsetup.controllers.tag_ctl_by_config(config)

    mw = MainWindow(
        info_ctl, tag_ctl, src_client, pkg_client,
        acceptable_source_name_extensions=(
            config['src_client']['acceptable_src_file_extensions']
            )
        )

    if isinstance(name_to_edit, str):
        if mw.load_data(os.path.basename(name_to_edit)) == 0:
            org.wayround.aipsetup.gtk.start_session()
    else:
        org.wayround.aipsetup.gtk.start_session()

    return
