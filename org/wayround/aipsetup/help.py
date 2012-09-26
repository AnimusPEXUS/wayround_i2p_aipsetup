
import os.path
import logging

import org.wayround.aipsetup
import org.wayround.aipsetup.modhelp
import org.wayround.utils.helprenderer


def aipsetup_help(opts, args):

    args_l = len(args)

    if args_l == 0:

        order = []
        items = org.wayround.aipsetup.modhelp.modules_tuple_list()
        for i in items:
            order.append(i[1]['short_name'])

        h = org.wayround.utils.helprenderer.render_help(
            org.wayround.aipsetup.modhelp.modules_dict(),
            order,
            only_titles=True,
            key=lambda x: x['module']
            )

        print("""\
Usage: aipsetup3 [module] [module_command] [command_parameters]

modules:

{}

    --help          See this help or help for module or command
    --version       Version Info
""".format(h)
   )


    else:
        if not args[0].isidentifier():
            raise ValueError("Wrong module name")

        if args_l > 1 and not args[1].isidentifier():
            raise ValueError("Wrong command name")

        d = org.wayround.aipsetup.modhelp.modules_dict()

        if not args[0] in list(d.keys()):
            logging.error("Have no module named `{}'".format(args[0]))
        else:
            try:
                exec("import org.wayround.aipsetup.{}".format(d[args[0]]['name']))
            except:
                logging.exception("Error importing module `{}'".format(d[args[0]]['name']))
            else:

                commands = None
                commands_order = None

                try:
                    commands = eval("org.wayround.aipsetup.{}.exported_commands()".format(d[args[0]]['name']))
                    commands_order = eval("org.wayround.aipsetup.{}.commands_order()".format(d[args[0]]['name']))
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
    'doc': eval("org.wayround.aipsetup.{}.__doc__".format(d[args[0]]['name']))
    })
    )

                if args_l == 2:

                    if not args[1] in commands:
                        logging.error("module `{}' have no command `{}'".format(args[0], args[1]))
                    else:

                        try:
                            help_text = eval("org.wayround.aipsetup.{}.exported_commands()['{}'].__doc__".format(d[args[0]]['name'], args[1]))
                        except:
                            logging.error("help text for command `{}' of module `{}' not available".format(args[1], args[0]))

                        else:
                            print(help_text)


