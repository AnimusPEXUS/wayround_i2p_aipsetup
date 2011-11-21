#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i686-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ cat ./DEFAULTS/Defaults.linux | sed -e "s#/opt/schily#/usr#g" > ./DEFAULTS/Defaults.linux2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '?',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ rm ./DEFAULTS/Defaults.linux # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '?',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mv ./DEFAULTS/Defaults.linux2 ./DEFAULTS/Defaults.linux # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '?',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cat ./DEFAULTS_ENG/Defaults.linux | sed -e "s#/opt/schily#/usr#g" > ./DEFAULTS_ENG/Defaults.linux2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '?',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ rm ./DEFAULTS_ENG/Defaults.linux # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '?',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mv ./DEFAULTS_ENG/Defaults.linux2 ./DEFAULTS_ENG/Defaults.linux # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '?',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cat ./DEFAULTS/Defaults.linux | sed -e "s#INS_BASE=       /opt/schily#INS_BASE=       \"$parent_dir/$new_base\"#" > ./DEFAULTS/Defaults.linux2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ rm ./DEFAULTS/Defaults.linux """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mv ./DEFAULTS/Defaults.linux2 ./DEFAULTS/Defaults.linux """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make install DESTDIR="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

