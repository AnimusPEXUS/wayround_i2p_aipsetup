#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ configure --with-apr=/usr/bin/apr-1-config --prefix=/usr/share/httpd --libdir=/usr/lib/http --datarootdir=/usr/share/httpd --bindir=/usr/bin --sbindir=/usr/sbin --mandir=/usr/share/man --includedir=/usr/include --oldincludedir=/usr/include --docdir=/usr/share/doc/httpd --dvidir=/usr/share/doc/httpd/dvi --pdfdir=/usr/share/doc/httpd/pdf --psdir=/usr/share/doc/httpd/ps --sysconfdir=/etc/httpd --localstatedir=/var --enable-shared --enable-modules=all --enable-mods-shared=all --enable-so --enable-cgi --enable-ssl --enable-http --enable-info --enable-proxy --enable-proxy-connect --enable-proxy-ftp --enable-proxy-http --enable-proxy-scgi --enable-proxy-ajp --enable-proxy-balancer  --host=i486-pc-linux-gnu --build=i486-pc-linux-gnu """,
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


        ]
    }

