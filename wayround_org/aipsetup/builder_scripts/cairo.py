

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            # '--enable-cogl',
            '--enable-directfb=auto',
            # '--enable-drm',
            '--enable-fc=auto',
            '--enable-ft=yes',
            '--enable-gl',
            '--enable-gallium=auto',
            #                    '--enable-glesv2',
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
            '--enable-gobject=yes',

            '--enable-egl',
            '--enable-glx',
            # '--enable-wgl',

            # xlib is deprecated
            #                    '--enable-xlib',
            #                    '--enable-xlib-xcb',
            #                    '--enable-xlib-xrender',

            '--disable-static',
            '--enable-xml=yes',

            '--with-x',
            ]
