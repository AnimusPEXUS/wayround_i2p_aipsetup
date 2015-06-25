
import glob
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()

        ret['after_distribute'] = self.builder_action_after_distribute

        return ret

    def builder_action_configure_define_options(self, called_as, log):
        ret = super().builder_action_configure_define_options(called_as, log)
        ret += [
            '--with-system-cairo',
            '--enable-gtk3',
            '--disable-gtk',
            '--without-junit',
            # TODO: track fixing of this
            '--with-system-npapi-headers=no',
            '--with-system-postgresql',
            #'--with-system-headers',
            
            ]
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = 0
        
        gid = glob.glob(wayround_org.utils.path.join(self.dst_dir, 'gid*'))

        lbo_dir = wayround_org.utils.path.join(
            self.dst_dir, 'multiarch', self.host, 'lib', 'libreoffice'
            )
        gid_dir = wayround_org.utils.path.join(lbo_dir, 'gid')
        lbo_lnk = wayround_org.utils.path.join(
            self.dst_dir, 'multiarch', self.host, 'bin', 'soffice'
            )

        try:
            os.makedirs(gid_dir)
        except:
            pass

        if not os.path.isdir(gid_dir):
            ret = 3
            logging.error(
                "Can't create required dir: `{}'".format(gid_dir)
                )

        else:
            logging.info("Moving gid* files")
            for i in gid:
                os.rename(
                    i,
                    wayround_org.utils.path.join(
                        gid_dir, os.path.basename(i)
                        )
                    )

            logging.info("Creating link")
            os.makedirs(
                wayround_org.utils.path.join(
                    self.dst_dir, 'multiarch', self.host, 'bin'
                    )
                )

            os.symlink(
                wayround_org.utils.path.relpath(
                    wayround_org.utils.path.join(
                        lbo_dir, 'program', 'soffice'
                        ),
                    os.path.dirname(lbo_lnk)
                    ),
                lbo_lnk
                )

        return ret


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute', 'afterdistribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--with-system-cairo',
                    '--enable-gtk3',
                    '--disable-gtk',
                    '--without-junit',
                    # TODO: track fixing of this
                    '--with-system-npapi-headers=no',
                    '--with-system-postgresql',
                    '--with-system-headers',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'afterdistribute' in actions and ret == 0:

            gid = glob.glob(wayround_org.utils.path.join(dst_dir, 'gid*'))

            lbo_dir = wayround_org.utils.path.join(
                dst_dir, 'usr', 'lib', 'libreoffice'
                )
            gid_dir = wayround_org.utils.path.join(lbo_dir, 'gid')
            lbo_lnk = wayround_org.utils.path.join(
                dst_dir, 'usr', 'bin', 'soffice'
                )

            try:
                os.makedirs(gid_dir)
            except:
                pass

            if not os.path.isdir(gid_dir):
                ret = 3
                logging.error(
                    "Can't create required dir: `{}'".format(gid_dir)
                    )

            else:
                logging.info("Moving gid* files")
                for i in gid:
                    os.rename(
                        i,
                        wayround_org.utils.path.join(
                            gid_dir, os.path.basename(i)
                            )
                        )

                logging.info("Creating link")
                os.makedirs(
                    wayround_org.utils.path.join(dst_dir, 'usr', 'bin')
                    )
                os.symlink(
                    wayround_org.utils.path.relpath(
                        wayround_org.utils.path.join(
                            lbo_dir, 'program', 'soffice'
                            ),
                        os.path.dirname(lbo_lnk)
                        ),
                    lbo_lnk
                    )

    return ret
