
import glob
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.archive
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = {}
        ret['pth_dir'] = \
            wayround_org.aipsetup.build.getDIR_PATCHES(
                self.buildingsite_path
                )

        # TODO: must be automatically
        ret['dst_lib_dir'] = \
            wayround_org.utils.path.join(
                self.calculate_dst_install_libdir()
                )
        ret['dst_share_dir'] = \
            wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'share'
            )
        ret['dst_pc_dir'] = \
            wayround_org.utils.path.join(
                ret['dst_share_dir'],
                'pkgconfig'
                )
        return ret

    def define_actions(self):
        ret = super().define_actions()
        ret['links'] = self.builder_action_links
        ret['pc'] = self.builder_action_pc
        return ret

    def builder_action_patch(self, called_as, log):

        ret = 0

        pth_dir = self.custom_data['pth_dir']

        pth_files = os.listdir(pth_dir)

        if len(pth_files) == 0:
            log.error("provide patches")
            ret = 30
        else:

            rolling = None

            patches = []

            for i in pth_files:
                if i.find('-patch.sh.') != -1 and not i.endswith('.asc'):
                    rolling = i
                    break

            for i in pth_files:
                if i.find('.patch.') != -1 and not i.endswith('.asc'):
                    patches.append(i)

            patches.sort()

            if rolling:

                compressor = (
                    wayround_org.utils.archive.
                    determine_compressor_by_filename(
                        rolling
                        )
                    )

                p = subprocess.Popen(
                    [compressor, '-kfd', rolling],
                    cwd=pth_dir
                    )
                if p.wait() != 0:

                    ret = 1

                else:
                    rolling = rolling[
                        0:
                        - len(
                            wayround_org.utils.archive.
                            determine_extension_by_filename(rolling)
                            )
                        ]

                    log.info(
                        "Applying rolling patch {}".format(rolling)
                        )

                    p = subprocess.Popen(
                        ['bash',
                         wayround_org.utils.path.join(pth_dir, rolling)],
                        cwd=self.get_src_dir(),
                        stdout=log.stdout,
                        stderr=log.stderr
                        )
                    p.wait()

        if ret == 0:

            for i in patches:

                compressor = (
                    wayround_org.utils.archive.
                    determine_compressor_by_filename(
                        i
                        )
                    )

                p = subprocess.Popen([compressor, '-kfd', i], cwd=pth_dir)
                if p.wait() != 0:

                    ret = 1

                else:
                    i = i[
                        0:
                        - len(
                            wayround_org.utils.archive.
                            determine_extension_by_filename(i)
                            )
                        ]

                    log.info("Applying weakly patch {}".format(i))

                    p = subprocess.Popen(
                        ['patch', '-p1', '-i',
                         wayround_org.utils.path.join(pth_dir, i)],
                        cwd=self.get_src_dir(),
                        stdout=log.stdout,
                        stderr=log.stderr
                        )
                    p.wait()
        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(
            called_as,
            log
            )

        ret += [
            '--enable-shared',
            '--enable-widec',
            '--enable-const',
            '--enable-ext-colors',
            '--enable-pc-files',
            '--with-shared',
            '--with-gpm',
            '--with-ticlib',
            '--with-termlib',
            '--with-pkg-config={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'share',
                    'pkgconfig'
                    )
                ),

            # NOTE: building with ada fails on new installations
            '--without-ada',
            ]

        if not self.get_is_crossbuild() and not self.get_is_crossbuilder():
            ret += [
                ]
        else:
            ret += [
                '--without-ada'
                ]

        return ret

    def builder_action_links(self, called_as, log):

        ret = 0

        dst_lib_dir = self.custom_data['dst_lib_dir']

        for s in [
                ('*w.so*', 'w.so', '.so'),
                ('*w_g.so*', 'w_g.so', '_g.so'),
                ('*w.a*', 'w.a', '.a'),
                ('*w_g.a*', 'w_g.a', '_g.a')
                ]:

            files = glob.glob(
                wayround_org.utils.path.join(dst_lib_dir, s[0])
                )

            for i in files:
                o_name = os.path.basename(i)
                l_name = o_name.replace(s[1], s[2])

                rrr = wayround_org.utils.path.join(dst_lib_dir, l_name)

                if os.path.exists(rrr):
                    os.unlink(rrr)
                os.symlink(o_name, rrr)

        links = os.listdir(dst_lib_dir)

        for i in links:

            flp = wayround_org.utils.path.join(dst_lib_dir, i)

            if os.path.islink(flp):

                rflp = wayround_org.utils.path.realpath(flp)
                r_name = os.path.basename(rflp)

                if os.path.exists(flp):
                    os.unlink(flp)
                os.symlink(r_name, flp)
        return ret

    def builder_action_pc(self, called_as, log):
        ret = 0

        dst_pc_lib_dir = self.custom_data['dst_pc_dir']

        if not os.path.isdir(dst_pc_lib_dir):
            raise Exception("`{}' dir is not exists".format(dst_pc_lib_dir))

        for s in [
                ('*w.pc', 'w.pc', '.pc'),
                ]:

            files = glob.glob(
                wayround_org.utils.path.join(dst_pc_lib_dir, s[0])
                )

            for i in files:
                o_name = os.path.basename(i)
                l_name = o_name.replace(s[1], s[2])

                rrr = wayround_org.utils.path.join(dst_pc_lib_dir, l_name)

                if os.path.exists(rrr):
                    os.unlink(rrr)
                os.symlink(o_name, rrr)
        return ret
