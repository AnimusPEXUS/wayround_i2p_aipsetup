
import os.path
import sys
import xml.sax.saxutils
import re


from . import file
from . import text
from . import error



def check_dictatorship_range(indict, debug=False):
    ret = 0

    if not isinstance(indict, dict):
        if debug:
            print("-e- Supplied data is not a dict")
        ret = 1
    else:

        for i in indict:
            if not isinstance(indict[i], dict):
                if debug:
                    print("-e- Dictatorship `%(name)s' element value is not a dict" % {
                        'name': i
                        })
                ret = 2
                break

    return ret


def check_dictatorship_unit(indict, debug=False, path=[]):

    ret = 0

    if len(path) >= 255:
        if debug:
            print("-e- Dictatorship tree recursion limit reached `%(path)s'" % {
                'path': '/'.join(path)
                })
        ret = 25

    # Supplied data defenetly must be a dict, othervice - error
    if ret == 0:
        if not isinstance(indict, dict):
            if debug:
                print("-e- Supplied data is not a dict")
            ret = 1

    if ret == 0:

        # 'type' must be supplied
        if not 'type' in indict:
            if debug:
                print("-e- Dictatorship unit type missing")
            ret = 2

        # 'type' must be one of following
        if ret == 0:
            if not indict['type'] in [
                'tag', 'dtd', 'comment', 'cdata', 'static',
                'pi', 'char'
                ]:
                if debug:
                    print("-e- Wrong dictatorship unit type")
                ret = 3

        if ret == 0:

            # If 'type' is 'tag', then check 'tag_info' and everything,
            # what underlie
            if indict['type'] == 'tag':
                if not 'tag_info' in indict \
                    or not isinstance(indict['tag_info'], dict):
                    if debug:
                        print("-e- Dictatorship unit type is `tag', but not `tag_info' supplied")
                    ret = 4

                else:
                    # tag name MUST be supplied and must be a string!
                    if not 'name' in indict['tag_info']:
                        if debug:
                            print("-e- `name' not supplied in dictatorship unit `tag_info'")
                        ret = 8
                    else:
                        if not isinstance(indict['tag_info']['name'], str):
                            if debug:
                                print("-e- tag `name' must be a string")
                            ret = 9

                    # attributes CAN be supplied or CAN be a None or a dict
                    if ret == 0:
                        if 'attributes' in indict['tag_info']:
                            if indict['tag_info']['attributes'] == None:
                                indict['tag_info']['attributes'] = {}
                            else:
                                if not isinstance(indict['tag_info']['attributes'], dict):
                                    if debug:
                                        print("-e- tag `attributes' must be dict")
                                    ret = 10
                                else:
                                    # attribute vailes can be a strings or callabels
                                    for i in indict['tag_info']['attributes']:
                                        if not isinstance(indict['tag_info']['attributes'][i], str):
                                            if debug:
                                                print("-e- tag `attributes' dict values must be strings")
                                            ret = 11
                                            break
                        else:
                            indict['tag_info']['attributes'] = {}

                    # 'tag_info' 'closed' attribute CAN be supplied and CAN be
                    #  None or bool.
                    if ret == 0:
                        if 'closed' in indict['tag_info']:
                            if not isinstance(indict['tag_info']['closed'], bool):
                                if debug:
                                    print("-e- tag `closed' attribute can be only bool")
                                ret = 13
                        else:
                            indict['tag_info']['closed'] = False


                    if ret == 0:
                        if 'css_placer' in indict['tag_info']:
                            if not isinstance(indict['tag_info']['css_placer'], bool):
                                if debug:
                                    print("-e- wrong `css_placer' type")
                                ret = 30
                        else:
                            indict['tag_info']['css_placer'] = False

                    if ret == 0:
                        if 'js_placer' in indict['tag_info']:
                            if not isinstance(indict['tag_info']['js_placer'], bool):
                                if debug:
                                    print("-e- wrong `js_placer' type")
                                ret = 31
                        else:
                            indict['tag_info']['js_placer'] = False

        if ret == 0:
            for i in ['required_css', 'required_js']:
                if i in indict:
                    if indict[i] == None:
                        ret = 0
                    elif not isinstance(indict[i], list):
                        if debug:
                            print("-e- `%(i)s' can be list or None" % {
                                'i': i
                                })
                        ret = 32
                    else:
                        for j in indict[i]:
                            if not isinstance(indict[i][j], str):
                                if debug:
                                    print("-e- All `%(i)s' values must be strings" % {
                                        'i': i
                                        })
                                ret = 33
                                break

                else:
                    indict[i] = None

            if ret != 0:
                break

        if ret == 0:
            if 'module' in indict:
                if not re.match(r'[a-zA-Z][\w-]*', indict['module']):
                    if debug:
                        print("-e- Wrong `module' name at `%(path)s'" % {
                            'path': '/'.join(path)
                            })
                    ret = 26
                if not 'uid' in indict:
                    if debug:
                        print("-e- `module' requires `uid' `%(path)s'" % {
                            'path': '/'.join(path)
                            })
                    ret = 28


        if ret == 0:
            if 'uid' in indict:
                if not re.match(r'[a-zA-Z][\w-]*', indict['uid']):
                    if debug:
                        print("-e- Wrong `uid' name at `%(path)s'" % {
                            'path': '/'.join(path)
                            })
                    ret = 27
                if not 'module' in indict:
                    if debug:
                        print("-e- `uid' requires `module' `%(path)s'" % {
                            'path': '/'.join(path)
                            })
                    ret = 29

        if ret == 0:
            if 'cache' in indict:
                if not isinstance(indict['cache'], bool):
                    if debug:
                        print("-e- wrong cache value")
                    ret = 5
            else:
                indict['cache'] = False

        if ret == 0:
            if indict['cache'] and not 'uid' in indict:
                if debug:
                    print("-e- cache requested, but not uid defined")
                ret = 23


        if ret == 0:
            if not 'content' in indict:
                indict['content'] = ''
                ret = 0
            elif indict['content'] == None:
                indict['content'] = ''
                ret = 0
            elif isinstance(indict['content'], (str, dict)):
                ret = 0
            else:
                if debug:
                    print("-e- wrong unit content value")
                ret = 7

        default_new_line_before_start = False
        default_new_line_before_content = False
        default_new_line_after_content = False
        default_new_line_after_end = False

        if indict['type'] == 'tag':
            default_new_line_before_start = True
            if indict['tag_info']['closed']:
                default_new_line_after_content = True
            else:
                if isinstance(indict['content'], dict):
                    default_new_line_after_content = True

        elif indict['type'] in ['tag', 'comment', 'dtd',
                                'pi']:
            default_new_line_after_end = True


        if ret == 0:
            for i in [('new_line_before_start', default_new_line_before_start),
                ('new_line_before_content', default_new_line_before_content),
                ('new_line_after_content', default_new_line_after_content),
                ('new_line_after_end', default_new_line_after_end)
                ]:
                if i[0] in indict:
                    if not isinstance(indict[i[0]], bool):
                        if debug:
                            print("-e- wrong `%(name)s' value type" % {
                                'name': i[0]
                                })
                        ret = 23
                        break
                else:
                    indict[i[0]] = i[1]

    return ret


def generate_attributes(indict, debug=False, path=[],
                        indent_size=2, tagname=''):
    ret = ''

    inaddr_l = len(path)

    indent = text.fill(' ', inaddr_l * indent_size)
    nameindent = text.fill(' ', len(tagname))

    attrs = []
    keys = list(indict.keys())
    keys.sort()
    for i in keys:

        if ret != '':
            ret += ' ';

        value = ''
        if isinstance(indict[i], str):
            value = indict[i]
        else:
            raise ValueError

        if isinstance(ret, str):


            try:
                attrs.append('%(name)s=%(value)s' % {
                    'name': i,
                    'value': xml.sax.saxutils.quoteattr(value)
                    })
            except:
                ret = 1
                break

    if isinstance(ret, str):
        ind_req = False
        for i in attrs:
            if len(i) > 80:
                ind_req = True
                break


        first = True
        for i in attrs:
            ind = ''
            if ind_req and not first:
                ind = "\n%(indent)s %(nameindent)s " % {
                    'indent': indent,
                    'nameindent': nameindent
                    }

            ret += "%(ind)s%(new_attr)s" % {
                'ind': ind,
                'new_attr': i
                }
            if first:
                first = False

    return ret


class XMLDictatorModulesDirError(Exception): pass


class XMLDictator:


    def __init__(self,
                 modules_dir,
                 xml_indent_size=2):

        if not os.path.isdir(modules_dir):
            raise XMLDictatorModulesDirError(
                "-e- modules dir `%(dirname)s' MUST exist" % {
                    'dirname': modules_dir
                    }
                )

        # path to dir with modules dirs
        self.modules_dir = os.path.abspath(modules_dir)

        # here linedup modules are listed. key is path
        self.units = {}

        # here will be stored
        self.tree_dict = {}

        # here are stored list of modules. keys are 
        # module names. eash module is dict of uid keys.
        # each uid key value is list of dictatorship 
        # unist
        self.modules = {}

        # those four attributes are for code formatting
        # purposes
        self.xml_indent_size = xml_indent_size
        self.xml_indent = text.fill(' ', xml_indent_size)

        self.css_indent_size = css_indent_size
        self.css_indent = text.fill(' ', css_indent_size)

        self.css_placer = None
        self.js_placer = None

        return

    def set_tree(self, indict):
        self.tree_dict = indict


    def get_module_dir(self, modulename):
        ret = os.path.join(self.modules_dir, modulename)

        if file.create_if_not_exists_dir(ret) != 0:
            ret = 1

        return ret

    def get_module_css_dir(self, modulename):
        ret = os.path.join(self.modules_dir, modulename, 'css')

        if file.create_if_not_exists_dir(ret) != 0:
            ret = 1

        return ret


    def _lineup_tree(self, indict, already_added, debug=False, path=[]):

        ret = 0

        keys = list(indict.keys())
        keys.sort()

        for i in keys:

            if not id(indict[i]) in already_added:

                tmp = '/'.join(path + [i])

                if not tmp in self.units:
                    self.units[tmp] = indict[i]

                del(tmp)

                already_added.add(id(indict[i]))


            if isinstance(indict[i]['content'], dict):
                if self._lineup_tree2(
                    indict[i]['content'], already_added, debug, path=path + [i]
                    ) != 0:
                    if debug:
                        print("-e- Inner tree lineup error error at `%(path)s'" % {
                            'path': '/'.join(path)
                            })
                    ret = 2

        return ret

    def lineup_tree(self, debug=False):
        self.units = {}
        already_added = set()
        return self._lineup_tree(
            self.tree_dict, already_added, debug, path=[]
            )

    def check_tree(self, debug=False):
        ret = 0
        for i in list(self.units.keys()).sort():
            if check_dictatorship_unit(self.units[i], debug, i.split('/')) != 0:
                if debug:
                    print("-e- Error while checking `%(path)s'" % {
                        'path': i
                        })
                ret = 1

        return ret


    def generate_module_map(self, debug=False):

        ret = 0

        self.units = {}

        for i in list(self.units.keys()).sort():

            if check_dictatorship_unit(
                self.units[i], debug, path=i.split('/')
                ) != 0:
                if debug:
                    print("-e- Dictatorshi check error at `%(path)s'" % {
                        'path': i
                        })
                ret = 1

            if ret == 0:

                if 'module' in self.units[i]:
                    if not self.units[i]['module'] in self.units:
                        self.units[self.units[i]['module']] = {}

                if 'uid' in self.units[i]:
                    if not self.units[i]['uid'] in self.units[self.units[i]['module']]:
                        self.units[self.units[i]['module']][self.units[i]['uid']] = self.units[i]

        return ret

    def find_placers(self, debug=False):

        self.css_placer = None
        self.js_placer = None

        for i in list(self.units.keys()).sort():

            if self.css_placer != None and self.js_placer != None:
                break

            if self.css_placer == None:
                if 'tag_info' in self.units[i] \
                    and 'css_placer' in self.units[i]['tag_info']:
                    self.css_placer = self.units[i]

            if self.js_placer == None:
                if 'tag_info' in self.units[i] \
                    and 'js_placer' in self.units[i]['tag_info']:
                    self.js_placer = self.units[i]

        return

    def place_css(self, debug=False):
        pass


    def _generate(self, root, indict, debug=False, path=[]):

        ret = ''

        keys = list(indict.keys())
        keys.sort()

        inaddr_l = len(path)

        indent = text.fill(' ', inaddr_l * self.xml_indent_size)

        for i in keys:

            if 'uid' in indict[i]:
                self.uids[indict[i]['uid']] = indict[i]

            if indict[i]['cache']:
                xml_cache_file_name = os.path.join(
                    self.xml_cache_dir,
                    indict[i]['uid'] + '.xml'
                    )

            rendered = ''
            if indict[i]['cache'] and os.path.exists(xml_cache_file_name):
                try:
                    f = open(xml_cache_file_name, 'r')
                    rendered = f.read()
                    f.close()
                except:
                    if debug:
                        print("-e- Can't load cache XML file `%(name)s'" % {
                            'name': xml_cache_file_name
                            })
                        error.print_exception_info(sys.exc_info())
                    ret = 2
                    break

            else:

                new_line_before_start = ''
                if indict[i]['new_line_before_start']:
                    new_line_before_start = '\n%(indent)s' % {
                        'indent': indent
                        }

                new_line_before_content = ''
                if indict[i]['new_line_before_content']:
                    new_line_before_content = '\n'

                new_line_after_content = ''
                if indict[i]['new_line_after_content']:
                    new_line_after_content = '\n%(indent)s' % {
                        'indent': indent
                        }

                new_line_after_end = ''
                if indict[i]['new_line_after_end']:
                    new_line_after_end = '\n'


                start = ''
                content = ''
                end = ''

                if indict[i]['type'] == 'comment':
                    start = '<!-- '

                    content = str(indict[i]['content'])

                    # NOTE: May be next line need to be reworked
                    content = content.replace('--', '-')

                    end = ' -->'

                elif indict[i]['type'] == 'pi':
                    start = '<?'
                    content = str(indict[i]['content'])
                    end = '?>'

                elif indict[i]['type'] == 'dtd':
                    start = '<!DOCTYPE '
                    content = str(indict[i]['content'])
                    end = '>'

                elif indict[i]['type'] == 'cdata':
                    start = '<![CDATA['
                    # NOTE: May be next line need to be reworked
                    content = str(indict[i]['content']).replace(']]>', '')
                    end = ']]>'

                elif indict[i]['type'] == 'char':
                    start = ''
                    content = xml.sax.saxutils.escape(str(indict[i]['content']))
                    end = ''

                elif indict[i]['type'] == 'static':
                    start = ''
                    content = indict[i]['content']
                    end = ''

                elif indict[i]['type'] == 'tag':

                    attributes = ''
                    if indict[i]['tag_info']['attributes'] != None:
                        attributes = generate_attributes(
                            indict[i]['tag_info']['attributes'], debug, path,
                            tagname=indict[i]['tag_info']['name']
                            )

                        if not isinstance(attributes, str):
                            ret = 1

                    if isinstance(ret, str):

                        closing_slash = ''
                        if indict[i]['tag_info']['closed']:
                            closing_slash = '/'

                        space_before_attributes = ''
                        if attributes != '':
                            space_before_attributes = ' '

                        space_before_closing_slash = ''
                        if closing_slash != '':
                            space_before_closing_slash = ' '

                        start = '<%(tagname)s%(space_before_attributes)s%(attributes)s%(space_before_closing_slash)s%(closing_slash)s>' % {
                            'tagname': indict[i]['tag_info']['name'],
                            'space_before_attributes': space_before_attributes,
                            'attributes': attributes,
                            'space_before_closing_slash': space_before_closing_slash,
                            'closing_slash': closing_slash
                            }

                        if not indict[i]['tag_info']['closed']:

                            if isinstance(indict[i]['content'], str):
                                content = indict[i]['content']
                            elif isinstance(indict[i]['content'], dict):
                                content = self._generate(
                                    root, indict[i]['content'], debug, path=path + [i]
                                    )
                            else:
                                content = str(indict[i]['content'])

                            end = '</%(tagname)s>' % {
                                'tagname': indict[i]['tag_info']['name']
                                }
                        else:
                            content = ''
                            end = ''

                else:
                    raise ValueError


                rendered = (""
                    + "%(new_line_before_start)s"
                    + "%(start)s"
                    + "%(new_line_before_content)s"
                    + "%(content)s"
                    + "%(new_line_after_content)s"
                    + "%(end)s"
                    + "%(new_line_after_end)s") % {
                    'new_line_before_start': new_line_before_start,
                    'new_line_before_content': new_line_before_content,
                    'new_line_after_content': new_line_after_content,
                    'new_line_after_end': new_line_after_end,
                    'start': start,
                    'content': content,
                    'end': end
                    }


                if indict[i]['cache']:
                    if not os.path.exists(xml_cache_file_name):
                        f = None
                        try:
                            f = open(xml_cache_file_name, 'w')
                        except:
                            if debug:
                                print("-e- Can't cache XML file `%(name)s'" % {
                                    'name': xml_cache_file_name
                                    })
                                error.print_exception_info(sys.exc_info())
                            ret = 1
                            break
                        else:
                            f.write(rendered)
                            f.close()

            ret += rendered

        return ret

    def generate(self, debug=False, generate_css=False, generate_js=False):

        ret = 0

        if self._check_tree(debug) != 0:
            if debug:
                print("-e- Some dictatorship errors found")
            ret = 1
        else:

            if isinstance(ret, str):
                if self._lineup_tree1(debug) != 0:
                    if debug:
                        print("-e- Some errors generating uid map")
                    ret = 3

            if isinstance(ret, str):
                if self._generate_module_map(debug) != 0:
                    if debug:
                        print("-e- Some errors generating module map")
                    ret = 4

            if isinstance(ret, str):
                ret = self._generate(
                    self.tree_dict, self.tree_dict, debug, path=[]
                    )

        return ret

def test():
    # Upper dict element with names (like folloving) is called
    # `dictatorship range'.
    # Dictatorship range's keys must point only on dict-s,
    # othervice it is an error.
    ret = ''
    a = {
        '000_xml_pi': {
            'type': 'pi',
            'content': 'xml version="1.1" encoding="UTF-8"',
            'cache': True,
            'uid': '4c890ca0-66fb-42ad-b519-d87811b695b3'
            },
        '010_xhtml_doctype': {
            'type': 'dtd',
            'content': 'html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"',
            'cache': True,
            'uid': 'e156ce9f-eaf4-4f24-96ca-594b3af0944b'
            },
        '100_html_tag': {
            # Dictatorship gange pointet dicts (like this)
            # is called `dictatorship unit'

            # Any dict can be one of folloving types:
            # 'tag', 'dtd', 'comment', 'cdata', 'static', 'char'
            # 'pi' (Processing instructions).
            # If type is 'tag',then 'tag_info' subdict is required
            'type': 'tag',

            # This can be required by other current dict elements or
            # settings like cache or css.
            # The uid is not required in every dict.
            # If uid is used by css, then "uid-%(uid)s" class
            # will be added to the tag.
            'uid': '55aeee15-ba79-4e78-a848-2c65c2e0d6a0',

            # inserts new lines
            # 'new_line_before_start': False,
            # 'new_line_before_content': False,
            # 'new_line_after_content': False,
            # 'new_line_after_end': False,

            # 'tag_info' required to present if type is 'tag'.
            # 'tag_info' must be a dict.
            'tag_info': {
                # any valid tag name
                'name': 'html',

                # None or dict
                # dict values must be strings 
                'attributes': {
                    'version': '-//W3C//DTD XHTML 1.1//EN',
                    'xmlns': 'http://www.w3.org/1999/xhtml',
                    'xml:lang': 'en',
                    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                    'xsi:schemaLocation': 'http://www.w3.org/1999/xhtml http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd'
                    },

                # (bool) if True - no contents is
                # passible and any info supplied in 'contents'
                # will be omited. Default is False.
                'closed': False
                },

            # None or bool. if is bool, then 'uid' is required
            'cache': True,

            # str, dict, None, callable
            # None - exchenged to empty string
            # string - used as is
            # dict - assumed tobe new
            # `dictatorship range'
            # callable - must return string
            'content': {
                '10_head': {
                    'type': 'tag',
                    'tag_info': {
                        'name': 'head',
                        'css_placer': True,
                        'js_placer': True
                        },
                    'content': {
                        'title': {
                            'type': 'tag',
                            'tag_info': {
                                'name': 'title'
                                },
                            'content': 'Page Title'
                            }
                        }
                    },
                '20_body': {
                    'type': 'tag',
                    'tag_info': {
                        'name': 'body'
                        },
                    'required_css': [],
                    'required_js': [],
                    }
                }

            }
        }

    print("Dictator test")
    b = XMLDictator(static_files_dir='/mnt/sda3/home/agu/p/aipsetup/tests/static',
                    css_cache_dir='/mnt/sda3/home/agu/p/aipsetup/tests/css-c',
                    xml_cache_dir='/mnt/sda3/home/agu/p/aipsetup/tests/xml-c')
    ret = b.generate(a, [], {}, True)

    return ret
