#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ bootstrap.sh """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some configure script error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ bjam --prefix=/usr """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some bjam error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ bjam --prefix="$bs_install_dir/usr" """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ pppp="`pwd`" ; cd $bs_install_dir/usr/include/ ; ln -s ./boost*/boost* ./boost ; cd "$pppp"  """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

