
import os
import os.path

__file__ = os.path.abspath(__file__)
PPWD = os.path.dirname(__file__)
PPWDl = len(PPWD)

def _scan(root_dir, f):

    files = os.listdir(root_dir)
    files.sort()

    isfiles = 0

    for each in files:
        full_path = os.path.join(root_dir, each)
        full_pathl = len(full_path)

        if not each[0] == '.' and os.path.isdir(full_path):
            _scan(full_path, f)

        elif not each[0] == '.' and os.path.isfile(full_path):
            p = full_path[PPWDl:]
            f.write('%(name)s\n' % {
                    'name': p
                    })



f=open('index.txt', 'w')

_scan(PPWD, f)

f.close()
exit(0)
