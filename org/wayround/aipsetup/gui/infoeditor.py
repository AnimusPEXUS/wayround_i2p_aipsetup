
from gi.repository import Gtk


class InfoEditorUi:

    def __init__(self):

        window = Gtk.Window()
        self.window = window

        main_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        main_box.set_margin_top(5)
        main_box.set_margin_start(5)
        main_box.set_margin_end(5)
        main_box.set_margin_bottom(5)
        window.add(main_box)

        refresh_list_button = Gtk.Button("Refresh")
        self.refresh_list_button = refresh_list_button
        save_button = Gtk.Button("Save")
        self.save_button = save_button

        show_not_filtered_button = Gtk.Button("Not Filtered")
        self.show_not_filtered_button = show_not_filtered_button

        show_filtered_button = Gtk.Button("Filtered")
        self.show_filtered_button = show_filtered_button

        quit_button = Gtk.Button("Quit")
        self.quit_button = quit_button

        main_button_box = Gtk.ButtonBox.new(Gtk.Orientation.VERTICAL)
        main_button_box.set_spacing(5)
        main_button_box.set_layout(Gtk.ButtonBoxStyle.START)

        main_button_box.pack_start(refresh_list_button, False, False, 0)
        main_button_box.pack_start(save_button, False, False, 0)
        main_button_box.pack_start(show_not_filtered_button, False, False, 0)
        main_button_box.pack_start(show_filtered_button, False, False, 0)
        main_button_box.pack_start(quit_button, False, False, 0)

        main_button_box.set_child_secondary(quit_button, True)

        paned1 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        tree_view1 = Gtk.TreeView()
        self.tree_view1 = tree_view1
        c = Gtk.TreeViewColumn("File Names")
        r = Gtk.CellRendererText()
        c.pack_start(r, True)
        c.add_attribute(r, 'text', 0)
        tree_view1.append_column(c)

        tree_view1_sw = Gtk.ScrolledWindow()
        tree_view1_sw.set_size_request(150, -1)
        tree_view1_sw.add(tree_view1)

        paned2 = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        paned2_box1 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        paned2_box1.pack_start(Gtk.Label("Name"), False, False, 0)
        self.name_entry = Gtk.Entry()
        paned2_box1.pack_start(self.name_entry, False, False, 0)

        paned2_box1.pack_start(Gtk.Label("BaseName"), False, False, 0)
        self.basename_entry = Gtk.Entry()
        paned2_box1.pack_start(self.basename_entry, False, False, 0)

        check_grid = Gtk.Grid()

        self.reducible_cb = Gtk.CheckButton.new_with_label("Reducible")
        self.removable_cb = Gtk.CheckButton.new_with_label("Removable")
        self.non_installable_cb = \
            Gtk.CheckButton.new_with_label("Non Installable")
        self.deprecated_cb = Gtk.CheckButton.new_with_label("Deprecated")

        check_grid.attach(self.reducible_cb, 0, 0, 1, 1)
        check_grid.attach(self.removable_cb, 1, 0, 1, 1)
        check_grid.attach(self.non_installable_cb, 0, 1, 1, 1)
        check_grid.attach(self.deprecated_cb, 1, 1, 1, 1)

        paned2_box1.pack_start(check_grid, False, False, 0)

        paned2_box1.pack_start(
            Gtk.Label("Installation Priority"), False, False, 0
            )

        adj = Gtk.Adjustment.new(5, 0, 10, 1, 1, 1)
        self.install_priority_scale = Gtk.Scale.new(
            Gtk.Orientation.HORIZONTAL,
            adj
            )
        self.install_priority_scale.set_round_digits(0)
        self.install_priority_scale.set_digits(0)
        self.install_priority_scale.set_draw_value(False)
        for i in range(10):
            self.install_priority_scale.add_mark(
                i,
                Gtk.PositionType.TOP,
                str(i)
                )

        paned2_box1.pack_start(self.install_priority_scale, False, False, 0)

        paned2_box1.pack_start(Gtk.Label("Home page"), False, False, 0)
        self.homepage_entry = Gtk.Entry()
        paned2_box1.pack_start(self.homepage_entry, False, False, 0)

        paned2_box1.pack_start(
            Gtk.Label("Build script name (without trailing .py)"),
            False, False, 0
            )
        self.buildscript_entry = Gtk.Entry()
        paned2_box1.pack_start(self.buildscript_entry, False, False, 0)

        paned2_box1.pack_start(Gtk.Label("Tags"), False, False, 0)

        self.tags_tw = Gtk.TextView()
        tags_tw_sw = Gtk.ScrolledWindow()
        tags_tw_sw.add(self.tags_tw)

        paned2_box1.pack_start(tags_tw_sw, True, True, 0)

        paned2_box2 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        exp_lab = Gtk.Label(
            """\
[+-] [(filename)|(version)|(status)] [!]COMPARATOR value

comparators:

  for status and filename:
    begins, contains, ends, fm, re

  for version:
    <, <=, ==, >=, >, re, fm, begins, contains, ends

'!' before comparator - means 'NOT'

warning:
when using status or version comparison,
algorithm uses not text in file name, but parsing result
so for name 'cgkit-2.0.0-py3k.tar.gz' parsing reult is:
{'groups': {'extension': '.tar.gz',
            'name': 'cgkit',
            'status': 'py.3.k',
            'status_dirty': 'py3k',
            'status_list': ['py', '3', 'k'],
            'status_list_dirty': ['py', '3', 'k'],
            'version': '2.0.0',
            'version_dirty': '2.0.0',
            'version_list': ['2', '0', '0'],
            'version_list_dirty': ['2', '.', '0', '.', '0']},
 'name': 'cgkit-2.0.0-py3k.tar.gz'}
"""
            )

        exp_lab.set_selectable(True)

        exp = Gtk.Expander()
        exp.set_label("(Help)")
        exp.add(exp_lab)

        filters_label_and_help = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)

        filters_label_and_help.pack_start(
            Gtk.Label("Filters"), False, False, 0
            )
        filters_label_and_help.pack_start(exp, False, False, 0)

        paned2_box2.pack_start(filters_label_and_help, False, False, 0)

        self.filters_tw = Gtk.TextView()
        filters_tw_sw = Gtk.ScrolledWindow()
        filters_tw_sw.add(self.filters_tw)
        paned2_box2.pack_start(filters_tw_sw, True, True, 0)

        paned2_box2.pack_start(Gtk.Label("Description"), False, False, 0)
        self.description_tw = Gtk.TextView()
        description_tw_sw = Gtk.ScrolledWindow()
        description_tw_sw.add(self.description_tw)
        paned2_box2.pack_start(description_tw_sw, True, True, 0)

        paned2_box1.set_size_request(150, -1)
        paned2_box2.set_size_request(150, -1)

        paned2.add1(paned2_box1)
        paned2.add2(paned2_box2)

        paned1.add1(tree_view1_sw)
        paned1.add2(paned2)

        main_box.pack_start(main_button_box, False, False, 0)
        main_box.pack_start(paned1, True, True, 0)

        main_box.show_all()

        return
