#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : True,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ echo "CFLAGS += -march=ia64 " > configparms # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : 'xxx',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --with-headers=/usr/src/headers/include --host=ia64-pc-linux-gnu --build=i486-pc-linux-gnu --target=i486-pc-linux-gnu --enable-kernel=2.6.30.7  --with-tls --with-elf """,
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
            'RUN'          : """ make install install_root="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

