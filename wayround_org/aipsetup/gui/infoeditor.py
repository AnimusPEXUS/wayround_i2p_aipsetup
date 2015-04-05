
from gi.repository import Gtk


class InfoEditorUi:

    def __init__(self):

        window = Gtk.Window()
        self.window = window
        window.set_default_size(800, 600)
        window.set_title("Package Information Editor")

        main_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        main_box.set_margin_top(5)
        main_box.set_margin_start(5)
        main_box.set_margin_end(5)
        main_box.set_margin_bottom(5)
        window.add(main_box)

        b2 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        b2.set_margin_top(5)
        b2.set_margin_start(5)
        b2.set_margin_end(5)
        b2.set_margin_bottom(5)

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

        mbb = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        mbb.pack_start(refresh_list_button, False, False, 0)
        mbb.pack_start(tree_view1_sw, True, True, 0)
        mbb.pack_start(quit_button, False, False, 0)

        b3 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        b3.set_margin_top(5)
        b3.set_margin_start(5)
        b3.set_margin_end(5)
        b3.set_margin_bottom(5)

        b3.pack_start(save_button, False, False, 0)
        b3.pack_start(show_not_filtered_button, False, False, 0)
        b3.pack_start(show_filtered_button, False, False, 0)

        notebook = Gtk.Notebook()
        self.notebook = notebook
        notebook.set_scrollable(True)
        notebook.set_tab_pos(Gtk.PositionType.LEFT)

        l = Gtk.Label("Main")
        l.set_alignment(0, 0.5)
        notebook.append_page(
            self._init_tab_main(),
            l
            )

        l = Gtk.Label("Source Paths")
        l.set_alignment(0, 0.5)
        notebook.append_page(
            self._init_tab_paths(),
            l
            )

        l = Gtk.Label("Filters")
        l.set_alignment(0, 0.5)
        notebook.append_page(
            self._init_tab_filter(),
            l
            )

        l = Gtk.Label("Tags")
        l.set_alignment(0, 0.5)
        notebook.append_page(
            self._init_tab_tags(),
            l
            )

        l = Gtk.Label("Dependencies")
        l.set_alignment(0, 0.5)
        notebook.append_page(
            self._init_tab_dependencies(),
            l
            )

        l = Gtk.Label("Description")
        l.set_alignment(0, 0.5)
        notebook.append_page(
            self._init_tab_description(),
            l
            )

        b2.pack_start(notebook, True, True, 0)
        b2.pack_start(b3, False, False, 0)

        main_box.pack_start(mbb, True, True, 0)
        main_box.pack_start(b2, True, True, 0)

        main_box.show_all()

        return

    def _init_tab_main(self):

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

        g = Gtk.Grid()
        g.set_column_spacing(5)
        g.set_row_spacing(5)
        # g.set_vexpand(True)
        # g.set_hexpand(True)
        # g.set_valign(Gtk.Align.FILL)
        # g.set_halign(Gtk.Align.FILL)

        b.pack_start(g, True, True, 0)

        l = Gtk.Label("Name")
        l.set_alignment(0, 0.5)
        g.attach(l, 0, 0, 1, 1)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_editable(False)
        self.name_entry.set_hexpand(True)
        g.attach(self.name_entry, 1, 0, 1, 1)

        l = Gtk.Label("BaseName")
        l.set_alignment(0, 0.5)
        g.attach(l, 0, 1, 1, 1)
        self.basename_entry = Gtk.Entry()
        self.basename_entry.set_hexpand(True)
        g.attach(self.basename_entry, 1, 1, 1, 1)

        self.reducible_cb = Gtk.CheckButton.new_with_label("Reducible")
        self.removable_cb = Gtk.CheckButton.new_with_label("Removable")
        self.non_installable_cb = \
            Gtk.CheckButton.new_with_label("Non Installable")
        self.deprecated_cb = Gtk.CheckButton.new_with_label("Deprecated")

        l = Gtk.Label("Home Page")
        l.set_alignment(0, 0.5)
        g.attach(l, 0, 2, 1, 1)
        self.homepage_entry = Gtk.Entry()
        self.homepage_entry.set_hexpand(True)
        g.attach(self.homepage_entry, 1, 2, 1, 1)

        l = Gtk.Label("Building Script Name (without trailing .py)")
        l.set_alignment(0, 0.5)
        g.attach(l, 0, 3, 1, 1)
        self.buildscript_entry = Gtk.Entry()
        self.buildscript_entry.set_hexpand(True)
        g.attach(
            self.buildscript_entry,
            1, 3, 1, 1
            )

        l = Gtk.Label("Tool For Version Valuing (without trailing .py)")
        l.set_alignment(0, 0.5)
        g.attach(l, 0, 4, 1, 1)
        self.version_tool_entry = Gtk.Entry()
        self.version_tool_entry.set_hexpand(True)
        g.attach(
            self.version_tool_entry,
            1, 4, 1, 1
            )

        g.attach(self.reducible_cb,
                 0, 5, 2, 1)
        g.attach(self.removable_cb,
                 0, 6, 2, 1)
        g.attach(self.non_installable_cb,
                 0, 7, 2, 1)
        g.attach(self.deprecated_cb,
                 0, 8, 2, 1)

        return b

    def _init_tab_filter(self):

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

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

        b.pack_start(exp, False, False, 0)

        self.filters_tw = Gtk.TextView()
        filters_tw_sw = Gtk.ScrolledWindow()
        filters_tw_sw.add(self.filters_tw)
        b.pack_start(filters_tw_sw, True, True, 0)

        return b

    def _init_tab_paths(self):
        return Gtk.Box()

    def _init_tab_dependencies(self):
        return Gtk.Box()

    def _init_tab_tags(self):

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

        self.tags_tw = Gtk.TextView()
        tags_tw_sw = Gtk.ScrolledWindow()
        tags_tw_sw.add(self.tags_tw)

        b.pack_start(tags_tw_sw, True, True, 0)

        return b

    def _init_tab_description(self):

        b = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

        self.description_tw = Gtk.TextView()

        description_tw_sw = Gtk.ScrolledWindow()

        description_tw_sw.add(self.description_tw)

        b.pack_start(description_tw_sw, True, True, 0)

        return b
