

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_patch(self, called_as, log):

        ret = 0

        '''
        NOTE: xmlcatalog command from vanilla libxml2-2.9.2.tar.gz has bug,
              which leads to incorrect work with xml catalog, which leads to
              damaged docbook installation

              following patch need to be appyed on libxml2-2.9.2 for xmlcatalog
              to work properly:

        sed \
          -e /xmlInitializeCatalog/d \
          -e 's/((ent->checked =.*&&/(((ent->checked == 0) ||\
                  ((ent->children == NULL) \&\& (ctxt->options \& XML_PARSE_NOENT))) \&\&/' \
          -i parser.c

            this patch is taken from here:
            http://www.linuxfromscratch.org/blfs/view/stable/general/libxml2.html
        '''

        info = self.get_package_info()

        if info['pkg_nameinfo']['groups']['version'] == '2.9.2':

            p = subprocess.Popen(
                [
                    'sed',
                    '-e', '/xmlInitializeCatalog/d',
                    '-e',
                    r's/((ent->checked =.*&&/(((ent->checked == 0) ||'
                    r'((ent->children == NULL) \&\& (ctxt->options \& '
                    r'XML_PARSE_NOENT))) \&\&/',
                    '-i', 'parser.c'
                ],
                cwd=self.get_src_dir()
                )
            ret = p.wait()

        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-python-install-dir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib',
                    'python2.7',
                    'site-packages'
                    ),
                ),
            '--with-python={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    ),
                ),
            'PYTHON={}'.format(
                wayround_org.utils.file.which(
                    'python',
                    self.calculate_install_prefix()
                    )
                )
            ]
        return ret
