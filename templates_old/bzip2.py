#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ make PREFIX=/usr CFLAGS="-Wall -Winline -O2 -g -D_FILE_OFFSET_BITS=64 -march=i486 -mtune=i486"  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make check """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make install PREFIX="$bs_install_dir/usr" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ make -f Makefile-libbz2_so CFLAGS="-Wall -Winline -O2 -g -D_FILE_OFFSET_BITS=64 -march=i486 -mtune=i486" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some lib make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cp -P *.so.* "$bs_install_dir/usr/lib" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some lib install error Makefile-libbz2_so',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cd "$bs_install_dir/usr/bin" ; aipsetup lf ; cd ~-  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : 'fix links errors',
            'EXITONERROR'  : False
            },


        ]
    }

