
'''
Edit package info on disk and update pkginfo database
'''

import collections
import functools
import glob
import logging
import os.path

from gi.repository import Gdk, Gtk

import wayround_org.aipsetup.controllers
import wayround_org.aipsetup.gtk
import wayround_org.aipsetup.gui.infoeditor
import wayround_org.aipsetup.info
import wayround_org.utils.gtk
import wayround_org.utils.list


class MainWindow:

    def __init__(
            self, info_ctl, src_client, pkg_client,
            acceptable_source_name_extensions
            ):

        self.info_ctl = info_ctl
        self.src_client = src_client
        self.pkg_client = pkg_client

        self.acceptable_source_name_extensions = (
            acceptable_source_name_extensions
            )

        self.currently_opened = None

        self.ui = wayround_org.aipsetup.gui.infoeditor.InfoEditorUi()

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

        self.ui.show_path_filtered_button.connect(
            'clicked',
            self.onShowPathFilteredSourceFilesButtonActivated
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

        filename = wayround_org.utils.path.join(
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
            data = wayround_org.aipsetup.info.read_info_file(filename)

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

                b = Gtk.TextBuffer()
                b.set_text('\n'.join(data['tags']))
                self.ui.tags_tw.set_buffer(b)

                b = self.ui.filters_tw.get_buffer()
                b.set_text(data['filters'])

                self.ui.basename_entry.set_text(str(data['basename']))

                self.ui.buildscript_entry.set_text(str(data['buildscript']))

                self.ui.removable_cb.set_active(bool(data['removable']))

                self.ui.reducible_cb.set_active(bool(data['reducible']))

                self.ui.non_installable_cb.set_active(
                    bool(data['non_installable'])
                    )

                self.ui.deprecated_cb.set_active(bool(data['deprecated']))

                self.ui.only_primary_install_cb.set_active(
                    bool(data['only_primary_install'])
                    )

                self.ui.source_path_prefixes_tw.get_buffer().set_text(
                    '\n'.join(data['source_path_prefixes'])
                    )

                self.ui.build_deps.set_values_list(
                    data['build_deps']
                    )

                self.ui.so_deps.set_values_list(
                    data['so_deps']
                    )

                self.ui.runtime_deps.set_values_list(
                    data['runtime_deps']
                    )

                self.currently_opened = os.path.basename(filename)
                
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

            filename = wayround_org.utils.path.join(
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
            tags = b.get_text(
                b.get_start_iter(),
                b.get_end_iter(),
                False
                )

            tags = tags.splitlines()

            tags = wayround_org.utils.list\
                .list_strip_remove_empty_remove_duplicated_lines(
                    tags
                    )

            data['tags'] = tags

            data['home_page'] = self.ui.homepage_entry.get_text()

            data['buildscript'] = self.ui.buildscript_entry.get_text()

            data['version_tool'] = self.ui.version_tool_entry.get_text()

            data['basename'] = self.ui.basename_entry.get_text()

            data['removable'] = self.ui.removable_cb.get_active()

            data['reducible'] = self.ui.reducible_cb.get_active()

            data['non_installable'] = self.ui.non_installable_cb.get_active()

            data['deprecated'] = self.ui.deprecated_cb.get_active()

            data['only_primary_install'] = \
                self.ui.only_primary_install_cb.get_active()

            data['source_path_prefixes'] = \
                self.ui.source_path_prefixes_tw.get_buffer().get_text(
                    self.ui.source_path_prefixes_tw.get_buffer(
                        ).get_start_iter(),
                    self.ui.source_path_prefixes_tw.get_buffer(
                        ).get_end_iter(),
                    False
                    ).split('\n')

            for i in range(len(data['source_path_prefixes']) - 1, -1, -1):
                if (
                        data['source_path_prefixes'][i].isspace()
                        or
                        data['source_path_prefixes'][i] == ''
                        ):
                    del data['source_path_prefixes'][i]

            for i in range(len(data['source_path_prefixes'])):
                data['source_path_prefixes'][i] =\
                    data['source_path_prefixes'][i].strip()

            data['build_deps'] = self.ui.build_deps.get_values_list()
            data['so_deps'] = self.ui.so_deps.get_values_list()
            data['runtime_deps'] = self.ui.runtime_deps.get_values_list()

            data['name'] = name

            if wayround_org.aipsetup.info.write_info_file(filename, data) != 0:
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

        mask = wayround_org.utils.path.join(
            self.info_ctl.get_info_dir(),
            '*.json')

        files = glob.glob(mask)

        files.sort()

        model = self.ui.tree_view1.get_model()
        model2 = self.ui.add_deps_list_tw.get_model()

        while len(model) != 0:
            model.remove(model.get_iter_first())

        while len(model2) != 0:
            model2.remove(model2.get_iter_first())

        for i in files:
            base = os.path.basename(i)
            model.append([base])
            model2.append([base[:-5]])

        if self.currently_opened:
            self.scroll_package_list_to_name(
                os.path.basename(self.currently_opened)
                )
        return

    def scroll_package_list_to_name(self, name):
        wayround_org.utils.gtk.list_view_select_and_scroll_to_name(
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
            wayround_org.aipsetup.gtk.stop_session()

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

        return

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

        return

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
                self.ui.basename_entry.get_text(),
                None
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
                wayround_org.utils.gtk.text_view(
                    '\n'.join(lst),
                    "{} - Non-filtered tarballs".format(
                        self.ui.name_entry.get_text()
                        )
                    )

        return

    def onShowPathFilteredSourceFilesButtonActivated(self, button):

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
                self.ui.basename_entry.get_text(),
                self.info_ctl.source_path_prefixes_db.get_object_tags(
                    self.ui.basename_entry.get_text()
                    )
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
                wayround_org.utils.gtk.text_view(
                    '\n'.join(lst),
                    "{} - Path-filtered tarballs".format(
                        self.ui.name_entry.get_text()
                        )
                    )

        return

    def onQuitButtonClicked(self, button):
        wayround_org.aipsetup.gtk.stop_session()
        return

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
                return wayround_org.utils.version.source_version_comparator(
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

                wayround_org.utils.gtk.text_view(
                    '\n'.join(lst),
                    "{} - Filtered tarballs".format(
                        self.ui.name_entry.get_text()
                        )
                    )

        return

    def onListRealoadButtonActivated(self, button):
        self.load_list()
        return

    def onPackageListItemActivated(self, view, path, column):

        sel = view.get_selection()

        model, itera = sel.get_selected()
        if not model is None and not itera is None:
            self.load_data(model[itera][0])

        return


def main(name_to_edit=None, config=None):

    info_ctl = wayround_org.aipsetup.controllers.info_ctl_by_config(config)

    src_client = wayround_org.aipsetup.controllers.src_client_by_config(config)

    pkg_client = wayround_org.aipsetup.controllers.pkg_client_by_config(config)

    mw = MainWindow(
        info_ctl, src_client, pkg_client,
        acceptable_source_name_extensions=(
            config['src_client']['acceptable_src_file_extensions'].split()
            )
        )

    if isinstance(name_to_edit, str):
        if mw.load_data(os.path.basename(name_to_edit)) == 0:
            wayround_org.aipsetup.gtk.start_session()
    else:
        wayround_org.aipsetup.gtk.start_session()

    return
