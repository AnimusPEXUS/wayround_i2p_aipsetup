#!/usr/bin/python

template={

    'PACKAGENAME'      : 'apache-ant',
    'PACKAGENAMESUFIX' : """ `date '+%Y%m%d%H%M%S'`-java-sun """,
    'SEPARATEDIR'      : False,
    'RELATIVE'         : '.',

    'stages'           : [

        {
            'RUN'          : """ build.sh """,
            'RELATIVELY'   : True,
            'ERRORMESSAGE' : '*** some build error',
            'EXITONERROR'  : True
            },

        {
            'RUN'          : """ mkdir -p "$bs_install_dir/usr/lib/apache-ant" ; cp -a dist/* "$bs_install_dir/usr/lib/apache-ant" ; mkdir -p "$bs_install_dir/etc/profile.d"  ; printf "export ANT_HOME=/usr/lib/apache-ant \nexport PATH=\"\$PATH:/usr/lib/apache-ant/bin\" \n " > "$bs_install_dir/etc/profile.d/apache-ant.sh" ; chmod 755 "$bs_install_dir/etc/profile.d/apache-ant.sh" ; mkdir -p "$bs_install_dir/usr/share/doc/apache-ant" ; cp -a docs/* "$bs_install_dir/usr/share/doc/apache-ant"  #  """,
            'RELATIVELY'   : False,
            'ERRORMESSAGE' : '*** some make error',
            'EXITONERROR'  : False
            },


        ]
    }

