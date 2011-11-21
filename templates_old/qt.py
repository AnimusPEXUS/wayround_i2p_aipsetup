#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ export CFLAGS=" -march=i486 -mtune=i486  " ; export CXXFLAGS=" -march=i486 -mtune=i486  " # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some configure script error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ ( ./configure -opensource -prefix /usr/lib/qt4 -sysconfdir /etc <<<yes )  """,
            'RELATIVELY'   : False,
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
            'RUN'          : """ make check """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ make install INSTALL_ROOT="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/etc/profile.d/SET" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ echo -en "#!/bin/bash\nexport PATH="\$PATH:/usr/lib/qt4/bin"\n export QTDIR=/usr/lib/qt4"\n export LD_LIBRARY_PATH="\$LD_LIBRARY_PATH:/usr/lib/qt4/lib" \n  " > "$bs_install_dir/etc/profile.d/SET/009.qt"  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

