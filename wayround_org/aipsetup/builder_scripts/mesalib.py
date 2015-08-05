

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        raise Exception("work out correct python settings")
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-texture-float',

            '--enable-gles1',
            '--enable-gles2',

            '--enable-openvg=auto',

            '--enable-osmesa',
            '--with-osmesa-bits=32',

            '--enable-xa',
            '--enable-gbm',

            # '--enable-egl',
            '--enable-gallium-egl',
            # '--enable-gallium-gbm',

            '--enable-dri',
            '--enable-dri3',

            # '--enable-glx-tls',

            '--enable-xorg',

            '--with-egl-platforms=x11,drm,null,wayland',


            '--with-gallium-drivers=nouveau,svga,swrast',
            '--with-dri-drivers=nouveau,i915,i965,r200,radeon,swrast',

            # '--enable-d3d1x',
            # '--enable-opencl',

            '--with-llvm-prefix={}'.format(self.host_multiarch_dir),
            
            # 'PYTHON2': self.
            ]

        return ret
