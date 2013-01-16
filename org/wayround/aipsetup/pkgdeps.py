
"""
Package dependecy tools
"""

import org.wayround.aipsetup.package

def get_asps_depending_on_asp(destdir, asp_name, mute):

    files = org.wayround.aipsetup.package.list_files_installed_by_asp(
        destdir, asp_name, mute
        )

    files = org.wayround.utils.path.prepend_path(files, destdir)

    files = org.wayround.utils.path.realpaths(files)

    elf_files = []

    # FIXME: finish

