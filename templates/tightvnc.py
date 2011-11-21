#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ xmkmf """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make World """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr/bin" "$bs_install_dir/usr/share/man"  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some mkdir error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ vncinstall "$bs_install_dir/usr/bin" "$bs_install_dir/usr/share/man"  """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

