#!/usr/bin/python

template={

    'PACKAGENAME'      : '',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-i486-pc-linux-gnu """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ bash jdk-*-i586.bin<<<yes """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ jdk=`find -maxdepth 1 -type d -name "jdk*"` ; jdk=`basename "$jdk"` ; bs_install_dir="$bs_run_dir/$jdk-$bs_pkg_sufix" ;  echo "jdk dir is $jdk" ; echo "New install dir is $bs_install_dir" ; mkdir -pv "$bs_install_dir/usr/lib/java" """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ cp -av "$jdk" "$bs_install_dir/usr/lib/java" """,
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
            'RUN'          : """ echo -en "#!/bin/bash\n export PATH="\$PATH:/usr/lib/java/$jdk/bin:/usr/lib/java/$jdk/jre/bin"\n export JAVA_HOME=/usr/lib/java/$jdk  " > "$bs_install_dir/etc/profile.d/SET/009.java"  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make install error',
            'EXITONERROR'  : True
            },


        ]
    }

