#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ make -f unix/Makefile generic CFLAGS=" -march=i486 -mtune=i486 " """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make check """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some prepair error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ make -f unix/Makefile install prefix="$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some install error',
            'EXITONERROR'  : True
            },


        ]
    }

