#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ make PREFIX=/usr """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr" "$bs_install_dir/usr/bin" "$bs_install_dir/usr/sbin" "$bs_install_dir/usr/lib" "$bs_install_dir/usr/include/gsm" "$bs_install_dir/usr/man/man1" "$bs_install_dir/usr/man/man8" "$bs_install_dir/usr/man/man3" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some mkdir error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make install INSTALL_ROOT="$bs_install_dir/usr" GSM_INSTALL_INC="$bs_install_dir/usr/include/gsm" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

