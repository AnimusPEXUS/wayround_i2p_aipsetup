
import os.path
import copy
import glob
import sys

import lxml.etree

import org.wayround.utils.error
import org.wayround.utils.file

import org.wayround.aipsetup.config
import org.wayround.aipsetup.router


from mako.template import Template

SAMPLE_PACKAGE_INFO_STRUCTURE = dict(
    # not required, but can be usefull
    homepage="",
    # description
    description="",
    # 'standard', 'local' or other package name
    pkg_name_type="",
    # string list
    tags=[],
    # string
    buildinfo=''
    )

pkg_info_file_template = Template(text="""\
<package>

  <!-- This file is generated by aipsetup -->

  <!-- name type can be 'standard', 'local' or other package name -->
  <nametype value="${ pkg_name_type | x}" />


  <description>${ description | x}</description>
  <homepage url="${ homepage | x}" />

  % if len(tags) == 0:
  <!-- Use <tag name="" /> constructions for listing
       tags -->
  % endif
  % for i in tags:
  <tag name="${ i | x}" />
  % endfor

  <buildinfo value="${ buildinfo | x }" />

</package>
""")

def router(opts, args):

    ret = org.wayround.aipsetup.router.router(
        opts, args, commands={
            'help': print_help,
            'mass_info_fix': mass_info_fix,
            'list': list_files,
            'edit': edit_file,
            'editor': editor,
            'copy': copy
            }
        )

    return ret

def print_help(opts, args):
    print("""\
aipsetup info command

    list            List xml files in info directory
    edit            Edit xml file from info directory with configured editor
    editor          Edit xml file with special editor
    copy            Make a copy of one xml file to new xml file name

    mass_info_fix   applayes fixes to info files

""")

def list_files(opts, args, typ='info'):
    mask = '*'

    args_l = len(args)

    if args_l > 2:
        print('-e- Too many parameters')
    else:

        if args_l > 1:
            mask = args[1]

        org.wayround.utils.file.list_files(
            org.wayround.aipsetup.config.config[typ], mask
            )

    return 0

def edit_file(opts, args, typ='info'):
    ret = 0
    if len(args) != 2:
        print("-e- builder to edit not specified")
        ret = 1
    else:
        ret = org.wayround.utils.edit.edit_file(
            '{}/{}'.format(
                org.wayround.aipsetup.config.config[typ],
                args[1]
                ),
            org.wayround.aipsetup.config.config['editor']
            )
    return ret

def editor(opts, args):
    import org.wayround.aipsetup.infoeditor

    org.wayround.aipsetup.infoeditor.main()

def copy(opts, args):
    if len(args) != 3:
        print("-e- wrong parameters count")
    else:

        org.wayround.utils.file.inderictory_copy_file(
            org.wayround.aipsetup.config.config['info'],
            args[1],
            args[2]
            )

def _find_latest(tree, tag, field):
    y = None
    x = tree.findall(tag)
    if len(x) > 0:
        y = x[-1].get(field)
    return y

def _find_list(tree, tag, field):
    y = []
    x = tree.findall(tag)
    lx = len(x)
    for i in range(lx):
        z = x[i].get(field)
        if isinstance(z, str):
            y.append(z)
    return y


def is_dicts_equal(d1, d2):

    ret = True

    for i in ['pkg_name_type', 'buildinfo',
              'homepage', 'description']:
        if d1[i] != d2[i]:
            ret = False
            break

    if ret:
        for i in ['tags']:

            if ret:
                for each in d1[i]:
                    if not each in d2[i]:
                        ret = False
                        break

            if ret:
                for each in d2[i]:
                    if not each in d1[i]:
                        ret = False
                        break

            if not ret:
                break

    return ret

def read_from_file(name):
    ret = None

    txt = ''
    tree = None

    try:
        f = open(name, 'r')
    except:
        print("-e- Can't open file %(name)s" % {
            'name': name
            })
        org.wayround.utils.error.print_exception_info(
            sys.exc_info()
            )
    else:
        txt = f.read()
        f.close()
        try:
            tree = lxml.etree.fromstring(txt)
        except:
            print("-e- Can't parse file `%(name)s'" % {
                'name': name
                })
            org.wayround.utils.error.print_exception_info(
                sys.exc_info()
                )
            ret = 2
        else:
            ret = copy.copy(SAMPLE_PACKAGE_INFO_STRUCTURE)

            for i in ['buildinfo']:
                x = _find_latest(tree, i, 'value')
                if x != None:
                    ret[i] = x

            x = _find_latest(tree, 'nametype', 'value')
            if x != None:
                ret['pkg_name_type'] = x

            x = _find_latest(tree, 'homepage', 'url')
            if x != None:
                ret['homepage'] = x

            x = tree.findall('description')
            if len(x) > 0:
                ret['description'] = x[-1].text

            ret['tags'] = _find_list(tree, 'tag', 'name')

            ret['tags'].sort()
            del(tree)

    return ret

def write_to_file(name, struct):

    ret = 0

    struct['tags'].sort()

    txt = pkg_info_file_template.render(
        pkg_name_type=struct['pkg_name_type'],
        description=struct['description'],
        homepage=struct['homepage'],
        tags=struct['tags'],
        buildinfo=struct['buildinfo']
        )

    try:
        f = open(name, 'w')
        f.write(txt)
        f.close()
    except:
        print("-e- Can't rewrite file %(name)s" % {
            'name': name
            })
        org.wayround.utils.error.print_exception_info(sys.exc_info())
        ret = 1

    return ret

def info_fixes(dicti, name):
    """
    This function is used by `mass_info_fix'

    Sometime it will contain checks and fixes for
    info files
    """

    if dicti['pkg_name_type'] == 'standard':

        pass

def mass_info_fix(opts, args):

    lst = glob.glob(os.path.join(org.wayround.aipsetup.config['info'], '*.xml'))

    for i in lst:

        name = os.path.basename(i)[:-4]

        dicti = read_from_file(i)

        info_fixes(dicti, name)

        write_to_file(i, dicti)

    print("-i- Processed %(n)d files" % {
        'n': len(lst)
        })

    return
