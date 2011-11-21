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
            'RUN'          : """ jdk=`find -maxdepth 1 -type d -name "jdk*"` ; jdk=`echo "$jdk" | sed -e "s/\.\///"` ; bs_install_dir="$bs_parent_dir/$jdk-$bs_pkg_sufix" ;  echo "jdk dir is $jdk" ; echo "New install dir is $bs_install_dir" ; mkdir -pv "$bs_install_dir/usr/lib/java" """,
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


        ]
    }

