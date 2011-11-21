#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-shared --with-shared --enable-widec --with-gpm --with-ticlib --with-termlib --enable-const --enable-ext-colors  --host=i486-pc-linux-gnu """,
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
            'RUN'          : """ cd "$bs_install_dir/usr/lib" ; cmdtmp1= ; cmdtmp2= ; cmdtmp1=`find -maxdepth 1 -name '*w.so*'` ; for cmdk in $cmdtmp1 ;  do  cmdtmp2=`echo "$cmdk" | sed -e 's/w\.so/\.so/g' `  ; ln -sf "$cmdk" "$cmdtmp2"  ; done ; unset cmdtmp1 ; unset cmdtmp2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** making simlinks error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cd "$bs_install_dir/usr/lib" ; cmdtmp1= ; cmdtmp2= ; cmdtmp1=`find -maxdepth 1 -name '*w_g.so*'` ; for cmdk in $cmdtmp1 ;  do  cmdtmp2=`echo "$cmdk" | sed -e 's/w_g\.so/_g\.a/so' `  ; ln -sf "$cmdk" "$cmdtmp2"  ; done ; unset cmdtmp1 ; unset cmdtmp2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** making simlinks error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cd "$bs_install_dir/usr/lib" ; cmdtmp1= ; cmdtmp2= ; cmdtmp1=`find -maxdepth 1 -name '*w.a*'` ; for cmdk in $cmdtmp1 ;  do  cmdtmp2=`echo "$cmdk" | sed -e 's/w\.a/\.a/g' `  ; ln -sf "$cmdk" "$cmdtmp2"  ; done ; unset cmdtmp1 ; unset cmdtmp2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** making simlinks error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cd "$bs_install_dir/usr/lib" ; cmdtmp1= ; cmdtmp2= ; cmdtmp1=`find -maxdepth 1 -name '*w_g.a*'` ; for cmdk in $cmdtmp1 ;  do  cmdtmp2=`echo "$cmdk" | sed -e 's/w_g\.a/_g\.a/g' `  ; ln -sf "$cmdk" "$cmdtmp2"  ; done ; unset cmdtmp1 ; unset cmdtmp2 # """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** making simlinks error',
            'EXITONERROR'  : True
            },


        ]
    }

