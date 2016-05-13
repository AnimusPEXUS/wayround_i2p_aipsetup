

import os.path

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [

            # NOTE: on OpenGL version printed by glxinfo or qtdiag
            #       http://permalink.gmane.org/gmane.comp.video.mesa3d.user/3311

            # ------------------------
            # next block is copy&paste from
            # https://wiki.freedesktop.org/nouveau/InstallNouveau/
            # ->
            '--enable-texture-float',
            '--enable-gles1',
            '--enable-gles2',
            '--enable-glx',
            '--enable-egl',
            '--enable-gallium-egl',
            '--enable-gallium-llvm',
            '--enable-shared-glapi',
            '--enable-gbm',
            '--enable-glx-tls',  # undefined reference to `_glapi_tls_Dispatch'
            '--enable-dri',
            '--enable-osmesa',
            '--enable-vdpau',
            #'--with-egl-platforms=x11,drm',
            #'--with-gallium-drivers=nouveau',
            #'--with-dri-drivers=nouveau',
            # <-
            # end of https://wiki.freedesktop.org/nouveau/InstallNouveau/
            # block
            # ------------------------

            # ------------------------
            # https://pkg-xorg.alioth.debian.org/howto/build-mesa.html
            # ->

            #'--with-dri-driverdir={}/lib/dri'.format(
            #    self.calculate_install_prefix()
            #    ),
            '--enable-driglx-direct',

            # <-
            # ------------------------

            #'--libdir={}/lib'.format(
            #    self.calculate_install_prefix()
            #    ),

            '--enable-texture-float',

            '--enable-gles1',
            '--enable-gles2',

            '--enable-openvg=auto',

            '--enable-osmesa',  # -
            '--with-osmesa-bits=64',  # -

            '--enable-xa',
            '--enable-gbm',

            #'--disable-gallium',
            #'--disable-gallium-llvm',

            '--enable-egl',
            '--enable-gallium-egl',  # -
            '--enable-gallium-gbm',

            '--enable-dri',  # -
            '--enable-dri3=auto',  # -

            # '--enable-glx-tls',

            '--enable-xorg',  # -

            '--with-egl-platforms=x11,drm,wayland',  # -


            '--with-gallium-drivers=nouveau,svga,swrast,virgl',  # -
            '--with-dri-drivers=nouveau,i915,i965,r200,radeon,swrast',  # -
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


            # NOTE: llvm is installed into 'lib' dir and
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
