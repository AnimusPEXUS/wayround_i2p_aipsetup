#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ make """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/boot" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/lib" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr/share/man/man9/" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make install INSTALL_PATH="$bs_install_dir/boot" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make modules_install INSTALL_MOD_PATH="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make firmware_install INSTALL_MOD_PATH="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make firmware_install INSTALL_MOD_PATH="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make mandocs """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ cp -v Documentation/DocBook/man/*.9.gz "$bs_install_dir/usr/share/man/man9/" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '***error',
            'EXITONERROR'  : False
            },


        ]
    }

