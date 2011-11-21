#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ make DESTDIRDEB="$bs_install_dir"  """,
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
            'RUN'          : """ make installdeb DESTDIRDEB="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -vp "$bs_install_dir/usr/sbin" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some mkdir error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mv -v "$bs_install_dir/etc/init.d/xrdp_control.sh" "$bs_install_dir/usr/sbin" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some mv error',
            'EXITONERROR'  : True
            },


        ]
    }

