

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

# TODO: configuration is quick hack. need to do better

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-nasm',
            '--disable-gtktest',
            #'--enable-decode-layer1',
            #'--enable-decode-layer2',
            #'--disable-frontend',
            'CFLAGS=-O2 -g -I{}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'include',
                    'ncursesw'
                    )
                ),
            'LDFLAGS=-ltinfow'
            ]

        if 'i686' in self.get_arch_from_pkgi():
            ret += [
                'host_cpu=i686',
                'ac_cv_header_xmmintrin_h=no',
                #'i686'
                ]

        #if 'i686' in self.get_arch_from_pkgi():
        #    ret += [
        #        'CFLAGS=-march=i486 -mtune=i486',
        #        ]
        # for i in range(len(ret)):
        #    if
        return ret
