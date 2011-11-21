#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : 'build_unix',

    'stages'           : [

        {
            'RUN'          : """ ../dist/configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-shared --enable-sql --enable-compat185 --enable-cxx --enable-tcl --with-tcl=/usr/lib --host=i486-pc-linux-gnu --build=i486-pc-linux-gnu  """,
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
            'RUN'          : """ mkdir -p "$bs_install_dir/usr/share/doc/db" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make install DESTDIR="$bs_install_dir" docdir="/usr/share/doc/db" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

