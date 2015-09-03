
import os.path
import shutil
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = dict()
        ret['makefile'] = wayround_org.utils.path.join(
            self.get_src_dir(), 'Makefile'
            )
        ret['zoneinfo'] = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'share',
            'zoneinfo'
            )
        ret['zoneinfop'] = wayround_org.utils.path.join(
            ret['zoneinfo'],
            'posix'
            )
        ret['zoneinfor'] = wayround_org.utils.path.join(
            ret['zoneinfo'],
            'right'
            )
        return ret

    def define_actions(self):
        ret = collections.OrderedDict([
            ('verify_tarball', self.builder_action_verify_tarball),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('distribute', self.builder_action_distribute)
            ])
        return ret

    def builder_action_verify_tarball(self, called_as, log):
        files = os.listdir(self.get_tar_dir())
        tzdata = None
        ret = 0

        for i in files:
            if i.startswith('tzdata'):
                tzdata = i
                break

        if tzdata is None:
            log.error("tzdata missing in tarball dir")
            log.error("It can be taken from IANA site")

            ret = 100

        return ret

    def builder_action_extract(self, called_as, log):

        ret = autotools.extract_high(
            self.buildingsite_path,
            'tzdata',
            log=log,
            unwrap_dir=False,
            rename_dir=False,
            more_when_one_extracted_ok=True
            )

        return ret

    def builder_action_configure(self, called_as, log):
        ret = 0

        try:
            f = open(self.custom_data['makefile'], 'r')
            txt = f.read()
            f.close()

            txt += """
printtdata:
\t\t@echo "$(TDATA)"
"""

            f = open(self.custom_data['makefile'], 'w')
            f.write(txt)
            f.close()
        except:
            log.exception("Can't do some actions on Makefile")
            ret = 1
        else:
            ret = 0

        return ret

    def builder_action_distribute(self, called_as, log):
        ret = 0

        os.makedirs(self.custom_data['zoneinfo'], exist_ok=True)
        os.makedirs(self.custom_data['zoneinfop'], exist_ok=True)
        os.makedirs(self.custom_data['zoneinfor'], exist_ok=True)

        zonefiles = []

        p = subprocess.Popen(
            ['make', 'printtdata'],
            cwd=self.get_src_dir(),
            stdout=subprocess.PIPE,
            stderr=log.stderr
            )
        r = p.wait()
        if r != 0:
            ret = r
        else:
            txt = str(p.stdout.read(), 'utf-8')
            zonefiles = txt.split(' ')
            zonefiles.sort()

            log.info("ZF: {}".format(', '.join(zonefiles)))

            for tz in zonefiles:

                log.info("Working with {} zone info".format(tz))

                p = subprocess.Popen(
                    ['zic',
                     '-L', '/dev/null',
                     '-d', self.custom_data['zoneinfo'],
                     '-y', 'sh yearistype.sh', tz],
                    cwd=self.get_src_dir(),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                p.wait()

                p = subprocess.Popen(
                    ['zic',
                     '-L', '/dev/null',
                     '-d', self.custom_data['zoneinfop'],
                     '-y', 'sh yearistype.sh', tz],
                    cwd=self.get_src_dir(),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                p.wait()

                p = subprocess.Popen(
                    ['zic',
                     '-L', 'leapseconds',
                     '-d', self.custom_data['zoneinfor'],
                     '-y', 'sh yearistype.sh', tz],
                    cwd=self.get_src_dir(),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                p.wait()

            for i in os.listdir(self.get_src_dir()):
                if i.endswith('.tab'):
                    shutil.copy(
                        wayround_org.utils.path.join(self.get_src_dir(), i),
                        wayround_org.utils.path.join(
                            self.custom_data['zoneinfo'],
                            i)
                        )

        return ret
