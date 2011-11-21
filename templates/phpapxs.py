#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ configure --enable-ftp --with-openssl --enable-mbstring --with-sqlite --enable-sqlite-utf8 --with-pdo-sqlite --with-gd --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-shared --with-jpeg-dir --with-png-dir --with-zlib-dir --with-ttf --with-freetype-dir  --with-apxs2 --with-pdo-pgsql --with-pgsql --with-mysql --with-ncurses --with-pdo-mysql --with-mysqli --with-readline  --host=i486-pc-linux-gnu --build=i486-pc-linux-gnu """,
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
            'RUN'          : """ make test """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/etc/httpd" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some check error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ echo -e "\n\nLoadModule rewrite_module modules/mod_rewrite.so\nLoadModule rewrite_module modules/mod_rewrite.so\n\n" > "$bs_install_dir/etc/httpd/httpd.conf" # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some install error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ make install INSTALL_ROOT="$bs_install_dir" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mv "$bs_install_dir/etc/httpd/httpd.conf" "$bs_install_dir/etc/httpd/httpd.conf.php" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some install error',
            'EXITONERROR'  : False
            },

        {
            'RUN'          : """ cd "$bs_install_dir" # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ find -maxdepth 1 -type d "(" -name ".channels" -o -name ".registry" ")" -print -exec rm -vr "{}" ";" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ find -maxdepth 1 -type f -name ".*" -print -exec rm "{}" ";" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

