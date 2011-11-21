#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ configure --with-termcap --enable-threads --with-ssl --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-shared --host=i486-pc-linux-gnu """,
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
            'RUN'          : """ mkdir -p "$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ export prefix="$bs_install_dir/usr" # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ make install prefix="$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cd "$bs_install_dir" ; aipsetup sfi ; cd ~- # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

