
import os.path
import logging

import org.wayround.aipsetup
import org.wayround.utils.helprenderer

def aipsetup_help(opts, args):

    args_l = len(args)

    if args_l == 0:
        for i in org.wayround.aipsetup.AIPSETUP_MODULES_LIST:
            exec("import org.wayround.aipsetup.{}".format(i))

        print("""\
Usage: aipsetup3 [module] [module_command] [command_parameters]

modules:

{g1}

{g2}

{g3}

{g4}

    --help          See this help or help for module or command
    --version       Version Info
""".format(
    g1=org.wayround.utils.helprenderer.render_help(
        {
            'info': org.wayround.aipsetup.info,
            'buildinfo': org.wayround.aipsetup.buildinfo,
            'constitution': org.wayround.aipsetup.constitution,
        },
        [
            'info',
            'buildinfo',
            'constitution'
        ],
        only_synopsis=True
        ),
    g2=org.wayround.utils.helprenderer.render_help(
        {
            'buildingsite': org.wayround.aipsetup.buildingsite,
            'build': org.wayround.aipsetup.build,
            'pack': org.wayround.aipsetup.pack,
            'package': org.wayround.aipsetup.package,
        },
        [
            'buildingsite',
            'build',
            'pack',
            'package'
        ],
        only_synopsis=True
        ),
    g3=org.wayround.utils.helprenderer.render_help(
        {
            'name': org.wayround.aipsetup.name,
            'docbook': org.wayround.aipsetup.docbook,
            'config': org.wayround.aipsetup.config
        },
        [
            'name',
            'docbook',
            'config'
        ],
        only_synopsis=True
        ),
    g4=org.wayround.utils.helprenderer.render_help(
        {
            'server': org.wayround.aipsetup.server,
            'client': org.wayround.aipsetup.client,
            'pkgindex': org.wayround.aipsetup.pkgindex
        },
        [
            'server',
            'client',
            'pkgindex'
        ]
        )
   )
)

    else:
        if not args[0].isidentifier():
            raise ValueError("Wrong module name")

        if args_l > 1 and not args[1].isidentifier():
            raise ValueError("Wrong module name")

        if not args[0] in org.wayround.aipsetup.AIPSETUP_MODULES_LIST:
            logging.error("Have no module named `{}'".format(args[0]))
        else:
            try:
                exec("import org.wayround.aipsetup.{}".format(args[0]))
            except:
                logging.exception("Error importing module `{}'".format(args[0]))
            else:

                commands = None
                commands_order = None

                try:
                    commands = eval("org.wayround.aipsetup.{}.exported_commands()".format(args[0]))
                    commands_order = eval("org.wayround.aipsetup.{}.commands_order()".format(args[0]))
                except:
                    pass

                if commands == None:
                    commands = []

                if commands_order == None:
                    commands_order = []


                if args_l == 1:

                    help_text = org.wayround.utils.helprenderer.render_help(
                        commands,
                        commands_order
                        )
                    print("""\
Usage: aipsetup3 {module} command

{doc}

Commands:

{text}
""".format_map({
    'module': args[0],
    'text': help_text,
    'doc': eval("org.wayround.aipsetup.{}.__doc__".format(args[0]))
    })
    )

                if args_l == 2:

                    if not args[1] in commands:
                        logging.error("module `{}' have no command `{}'".format(args[0], args[1]))
                    else:

                        try:
                            help_text = eval("org.wayround.aipsetup.{}.exported_commands()['{}'].__doc__".format(args[0], args[1]))
                        except:
                            logging.error("help text for command `{}' of module `{}' not available".format(args[1], args[0]))

                        else:
                            print(help_text)


