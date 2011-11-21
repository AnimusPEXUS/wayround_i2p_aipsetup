#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-shared --host=i486-pc-linux-gnu --build=i486-pc-linux-gnu """,
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

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr/include/pygtk" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some mkdir error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cp -a gtk/*.h "$bs_install_dir/usr/include/pygtk" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some copy error',
            'EXITONERROR'  : True
            },


        ]
    }

