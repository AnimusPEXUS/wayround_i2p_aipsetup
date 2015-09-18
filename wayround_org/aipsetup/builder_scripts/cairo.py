

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            #'--enable-cogl=auto',
            '--enable-directfb=auto',
            #'--enable-drm=auto',
            '--enable-fc',
            '--enable-ft',
            '--enable-gl',
            #'--enable-gallium',
            #'--enable-glesv2',
            '--enable-pdf=yes',
            '--enable-png=yes',
            '--enable-ps=yes',
            '--enable-svg=yes',
            #                    '--enable-qt',

            '--enable-quartz-font=auto',
            '--enable-quartz-image=auto',
            '--enable-quartz=auto',

            '--enable-script=yes',


            '--enable-tee=yes',
            '--enable-vg=auto',
            '--enable-wg=auto',
            '--enable-xcb',
            '--enable-xcb-shm',
            '--enable-xlib-xcb',
            '--enable-gobject=auto',

            '--enable-egl=auto',
            '--enable-glx=auto',
            #'--enable-wgl',

            # xlib is deprecated
            #                    '--enable-xlib',
            #                    '--enable-xlib-xcb',
            #                    '--enable-xlib-xrender',

            '--disable-static',
            '--enable-xml=yes',

            '--with-x',
            #'WERROR='
            ]
