
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.archive
import wayround_org.utils.file


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {}

    def builder_action_extract(self, called_as, log):
        files = os.listdir(self.get_tar_dir())

        tcl_found = False
        tk_found = False
        for i in files:
            if i.startswith('tcl'):
                tcl_found = i

            if i.startswith('tk'):
                tk_found = i

        if not tcl_found:
            log.error(
                "Tcl and Tk source tarballs must be in tarballs dir"
                )
            ret = 20
        else:

            log.info("Extracting Tcl")
            wayround_org.utils.archive.extract(
                wayround_org.utils.path.join(self.get_tar_dir(), tcl_found),
                self.buildingsite_path,
                log=log,
                )

            log.info("Extracting Tk")
            wayround_org.utils.archive.extract(
                wayround_org.utils.path.join(self.get_tar_dir(), tk_found),
                self.buildingsite_path,
                log=log
                )

            ret = super().builder_action_extract(called_as, log)
        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-threads',
            '--enable-wince',
            ]

        if self.get_arch_from_pkgi().startswith('x86_64'):
            ret += [
                '--enable-64bit',
                '--enable-64bit-vis',
                ]

        return ret
