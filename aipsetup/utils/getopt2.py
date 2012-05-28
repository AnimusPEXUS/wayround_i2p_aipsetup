
def getopt(args):
    """
    Parser for command line options

    It's not compatible with CPython getopt module.

    It's work differently in many ways.

    Parameter must be list of strings -- Simple sys.argv will do.

    Example:

       getopt2.getopt(['a', 'b', 'c', 'd=123', 'dd=123', '-a',
                       '3', '-b=3', '--c=4', '--long=5',
                       '---strange=6', '--', '-e=7'])

       ([('-a', None),
         ('-b', '3'),
         ('--c', '4'),
         ('--long', '5'),
         ('---strange', '6')],
        ['a', 'b', 'c', 'd=123', 'dd=123', '3', '-e=7'])

    """


    ret_args = []

    ret_opts = []

    if not isinstance(args, list):
        raise TypeError

    all_args = False

    len_args = len(args)

    i = 0

    while True:

        if i == len_args:
            break

        if all_args:

            ret_args.append(args[i])

        else:

            args_i_len = len(args[i])

            if args_i_len > 1:

                if args[i] == '--':
                    all_args = True
                else:

                    if args[i].startswith('-'):

                        eq_pos = args[i].find('=')
                        if eq_pos != -1:
                            ret_opts.append((args[i][:eq_pos], args[i][eq_pos+1:]))
                        else:
                            ret_opts.append((args[i], None))

                    else:
                        ret_args.append(args[i])


            else:
                ret_args.append(args[i])

        i += 1

    return ret_opts, ret_args
