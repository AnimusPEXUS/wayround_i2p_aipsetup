#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : 'src',

    'stages'           : [

        {
            'RUN'          : """ make CFLAGS=" -Wall -O2 -fomit-frame-pointer -D_GNU_SOURCE -march=i486 -mtune=i486" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/bin" "$bs_install_dir/sbin" "$bs_install_dir/usr/bin" "$bs_install_dir/usr/sbin" "$bs_install_dir/usr/share/man/man1" "$bs_install_dir/usr/share/man/man5" "$bs_install_dir/usr/share/man/man8" "$bs_install_dir/usr/include" "$bs_install_dir/dev" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make install ROOT="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

