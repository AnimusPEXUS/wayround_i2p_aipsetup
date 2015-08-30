

import os.path

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-texture-float',

            '--enable-gles1',
            '--enable-gles2',

            '--enable-openvg=auto',

            '--enable-osmesa', #-
            '--with-osmesa-bits=64', #-

            '--enable-xa',
            '--enable-gbm',

            #'--disable-gallium',
            #'--disable-gallium-llvm',

             '--enable-egl',
            '--enable-gallium-egl', #-
             '--enable-gallium-gbm',

            '--enable-dri', #-
            '--enable-dri3', #-

            '--enable-glx-tls',

            '--enable-xorg', #-

            '--with-egl-platforms=x11,drm,wayland', #-


            '--with-gallium-drivers=nouveau,svga,swrast',#-
            '--with-dri-drivers=nouveau,i915,i965,r200,radeon,swrast',#-
            #'--without-gallium-drivers',
            #'--without-dri-drivers',

            # '--enable-d3d1x',
            # '--enable-opencl',

            #'--with-clang-libdir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'lib'
            #        )
            #    ),
            #'--with-llvm-prefix={}'.format(self.get_host_dir()),

            #'PYTHON2={}'.format(
            #    wayround_org.utils.file.which(
            #        'python2',
            #        self.get_host_dir()
            #        )
            #    )


            # NOTE: By default llvm is installed into 'lib' dir and
            #       trying to use 32-bit glibc libs, while it must use
            #       64-bit. so here is the hack to point it to right
            #       'lib64' dir
            'LLVM_LDFLAGS=-L{}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_libdir(),
                    #'lib'
                    )
                ),
            ]

        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += [
            'LLVM_LDFLAGS=-L{}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_libdir(),
                    #'lib'
                    )
                ),
        ]
        return ret
    
