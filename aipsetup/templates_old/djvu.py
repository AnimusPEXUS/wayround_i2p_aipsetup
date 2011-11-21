#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i686-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ export CFLAGS=" -O2 -march=i686 -mtune=i686 " ; export CPPFLAGS=" -O2 -march=i686 -mtune=i686 " ; export CXXFLAGS=" -O2 -march=i686 -mtune=i686 "  #  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-shared --host=i686-pc-linux-gnu """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some configure script error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make """,
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

