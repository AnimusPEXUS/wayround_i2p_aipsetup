#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-hdr-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make headers_install INSTALL_HDR_PATH="$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },


        ]
    }

