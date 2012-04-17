
import glob
import os
import os.path
import subprocess

def print_help():
    print """\
aipsetup builders command

   list [MASK]

   copy NAME1 NAME2

   edit NAME

"""

def router(opts, args, config):

    ret = 0

    args_l = len(args)

    if args_l == 0:
        print "-e- command not given"
        ret = 1

    else:

        if args[0] == 'help':
            print_help()
        
        elif args[0] == 'list':
            mask = '*'

            if args_l > 1:

                if args_l > 2:
                    print '-e- Too many parameters'
                else:
                    mask = args[1]

            lst = glob.glob('%(path)s/%(mask)s' % {
                    'path': config['builders'],
                    'mask': mask
                    })

            lst.sort()

            semi = ''
            if len(lst) > 0:
                semi = ':'

            print 'found %(n)s builder(s)%(s)s' % {
                'n': len(lst),
                's': semi
                }

            for each in lst:
                print os.path.basename(each)


        elif args[0] == 'edit':
            if args_l != 2:
                print "-e- builder to edit not specified"
            else:
                p = None
                try:
                    p = subprocess.Popen([config['editor'], '%(path)s/%(file)s' % {
                                'path': config['builders'],
                                'file': args[1]
                                }])
                except:
                    print '-e- error starting editor'
                else:
                    try:
                        p.wait()
                    except:
                        print '-e- error waiting for editor'

                    print '-i- editor exited'

                del(p)

        elif args[0] == 'copy':
            if args_l != 3:
                print "-e- wrong parameters count"
            else:

                folder = config['builders']

                f1 = os.path.join(folder, args[1])
                f2 = os.path.join(folder, args[2])

                if os.path.isfile(f1):
                    if os.path.exists(f2):
                        print "-e- destination already exists"
                    else:
                        print "-i- copying %(f1)s to %(f2)s" % {
                            'f1': f1,
                            'f2': f2
                            }
                        shutil.copy(f1, f2)
                else:
                    print "-e- source builder not exists"


        elif args[0] == 'use':

            print "-e- TODO: Impliment"

        else:
            print "-e- wrong command. try aipsetup builders help"

    return ret
