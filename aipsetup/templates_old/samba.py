#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : True,
    'RELATIVE'         : 'source3',

    'stages'           : [

        {
            'RUN'          : """ configure --with-pam --with-pam_smbpass --enable-fhs --with-swatdir=/usr/share/samba/swat --prefix=/usr --localstatedir=/var --sysconfdir=/etc/samba --libexecdir=/usr/libexec --libdir=/usr/lib --with-configdir=/etc/samba --with-privatedir=/etc/samba/private --includedir=/usr/include --datarootdir=/usr/share --host=i486-pc-linux-gnu --build=i486-pc-linux-gnu """,
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
            'RUN'          : """ make check """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ make install DESTDIR="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cp -a "$bs_run_dir/examples" "$bs_run_dir/docs" "$bs_install_dir/usr/share/samba" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

