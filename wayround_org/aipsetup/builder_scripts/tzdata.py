
import logging
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
        ret['makefile'] = os.path.join(self.src_dir, 'Makefile')
        ret['zoneinfo'] = os.path.join(self.dst_dir, 'usr', 'share', 'zoneinfo')
        ret['zoneinfop'] = os.path.join(ret['zoneinfo'], 'posix')
        ret['zoneinfor'] = os.path.join(ret['zoneinfo'], 'right')
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

    def builder_action_verify_tarball(self):
        files = os.listdir(self.tar_dir)
        tzdata = None
        ret = 0

        for i in files:
            if i.startswith('tzdata'):
                tzdata = i
                break

        if tzdata is None:
            logging.error("tzdata missing in tarball dir")
            logging.error("It can be taken from IANA site")

            ret = 100

        return ret

    def builder_action_extract(self):

        ret = autotools.extract_high(
            self.buildingsite,
            'tzdata',
            unwrap_dir=False,
            rename_dir=False,
            more_when_one_extracted_ok=True
            )

        return ret

    def builder_action_configure(self):
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
            logging.exception("Can't do some actions on Makefile")
            ret = 1
        else:
            ret = 0

        return ret

    def builder_action_distribute(self):
        ret = 0

        os.makedirs(self.custom_data['zoneinfo'])
        os.makedirs(self.custom_data['zoneinfop'])
        os.makedirs(self.custom_data['zoneinfor'])

        zonefiles = []

        p = subprocess.Popen(
            ['make', 'printtdata'],
            cwd=self.src_dir,
            stdout=subprocess.PIPE
            )
        r = p.wait()
        if r != 0:
            ret = r
        else:
            txt = str(p.stdout.read(), 'utf-8')
            zonefiles = txt.split(' ')
            zonefiles.sort()

            logging.info("ZF: {}".format(', '.join(zonefiles)))

            for tz in zonefiles:

                logging.info("Working with {} zone info".format(tz))

                p = subprocess.Popen(
                    ['zic',
                     '-L', '/dev/null',
                     '-d', self.custom_data['zoneinfo'],
                     '-y', 'sh yearistype.sh', tz],
                    cwd=self.src_dir
                    )
                p.wait()

                p = subprocess.Popen(
                    ['zic',
                     '-L', '/dev/null',
                     '-d', self.custom_data['zoneinfop'],
                     '-y', 'sh yearistype.sh', tz],
                    cwd=self.src_dir
                    )
                p.wait()

                p = subprocess.Popen(
                    ['zic',
                     '-L', 'leapseconds',
                     '-d', self.custom_data['zoneinfor'],
                     '-y', 'sh yearistype.sh', tz],
                    cwd=self.src_dir
                    )
                p.wait()

            for i in os.listdir(self.src_dir):
                if i.endswith('.tab'):
                    shutil.copy(
                        os.path.join(self.src_dir, i),
                        os.path.join(self.custom_data['zoneinfo'], i)
                        )

        return ret
