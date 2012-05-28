# -*- coding: utf-8 -*-

def edit_file(config, filename, what):
    return edit_file_direct(config, '%(path)s/%(file)s' % {
            'path': config[what],
            'file': filename
            })


def edit_file_direct(config, filename):
    p = None
    try:
        p = subprocess.Popen([config['editor'],
                                            '%(file)s' % {
                                                'file': filename
                                                }]
                                            )
    except:
        print '-e- error starting editor'
        print_exception_info(sys.exc_info())
    else:
        try:
            p.wait()
        except:
            print '-e- error waiting for editor'

        print '-i- editor exited'

    del(p)

    return


