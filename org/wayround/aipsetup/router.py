
import logging

def router(opts, args, commands={}):

    ret = 0

    args_l = len(args)

    if args_l == 0:
        logging.error("Command not Given")
        ret = 1
    else:

        if not args[0] in commands:
            logging.error("Wrong Command")
        else:
            ret = commands[args[0]](opts, args)

    return ret
