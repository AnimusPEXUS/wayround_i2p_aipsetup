
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = {
            'apr_1_config': wayround_org.utils.file.which(
                'apr-1-config',
                '/multiarch/{}'.format(self.host)
                )
            }
        if ret['apr_1_config'] is None:
            raise Exception("`apr-1-config' not installed on system")
        return ret

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(
            called_as,
            log) + [
                '--with-apr=' + self.custom_data['apr_1_config'],


            '--enable-shared',
            '--enable-modules=all',
            '--enable-mods-shared=all',
            '--enable-so',
            '--enable-cgi',
            '--enable-ssl',
            '--enable-http',
            '--enable-info',
            '--enable-proxy',
            '--enable-proxy-connect',
            '--enable-proxy-ftp',
            '--enable-proxy-http',
            '--enable-proxy-scgi',
            '--enable-proxy-ajp',
            '--enable-proxy-balancer',
                ]
