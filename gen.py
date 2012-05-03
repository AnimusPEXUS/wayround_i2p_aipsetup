
import pkgutil
import os
import os.path
import fnmatch
import copy
import sys

def walk_package(name):

    modules = []
    packages = []

    exec("import %(name)s" % {'name': name})

    for i in pkgutil.walk_packages(eval("%(name)s.__path__" % {'name': name})):

        name2 = name + '.' + i[1]

        # print "-i- Importing %(name)s" % {'name': name2}
        try:
            exec("import %(name)s" % {'name': name2})
        except:
            print "-e- Can't import %(name)s" % {'name': name2}
        else:
            if fnmatch.fnmatch(os.path.basename(eval("%(name)s.__file__" % {'name': name2})), '__init__.py?'):
                print "-i- Found package %(name)s" % {'name': name2}
                packages.append(name2)
            else:
                print "-i- Found module %(name)s" % {'name': name2}
                modules.append(name2)
#            exec("del(%(name)s)" % {'name': name2})

#    exec("del(%(name)s)" % {'name': name})

    return packages, modules


def walk_iter(ready_modules, package_list):

    for i in copy.copy(package_list):
        p = []
        m = []
        try:
            p, m = walk_package(i)
        except:
            print "-e- Error walking package %(name)s" % {'name': i}
        else:
            package_list += p

            ready_modules += [i]
            ready_modules += m

        finally:
            if i in package_list:
                package_list.remove(i)

    return

package_list = sys.argv[1:]

ready_modules = []

while len(package_list) > 0:
    walk_iter(ready_modules, package_list)
    package_list = list(set(package_list))
    package_list.sort()

ready_modules = list(set(ready_modules))
ready_modules.sort()

print "Creating doc for: %(list)s ." % {'list': ', '.join(ready_modules)}

modules_str = " "

for i in ready_modules:
    modules_str += " '%(name)s' " % {'name': i}

os.system("epydoc -v --show-sourcecode --show-private --show-imports --graph=all %(names)s " % {'names': modules_str})
