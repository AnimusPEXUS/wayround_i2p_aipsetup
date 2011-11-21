#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i686-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ configure --prefix=/usr --enable-gui --enable-radio --enable-radio-capture --enable-radio-v4l2 --enable-tv --enable-tv-v4l1 --enable-tv-v4l2 --enable-vcd  --enable-freetype --enable-ass --enable-gif --enable-png --enable-mng --enable-jpeg --enable-real --enable-xvid-lavc --enable-x264-lavc --extra-cflags="`pkg-config --cflags libass`" --extra-ldflags="`pkg-config --libs libass`"  """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some configure script error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make LDFLAGS="`pkg-config --libs libass`" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make check """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ make install DESTDIR="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

