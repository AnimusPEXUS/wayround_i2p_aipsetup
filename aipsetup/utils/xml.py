# -*- coding: utf-8 -*-


import os.path
import sys
import xml.sax.saxutils
import re
import urllib.parse


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

class ExceptionDictatorshipUnitTooDeep(Exception): pass
class ExceptionMissingDictatorshipUnitAttribute(Exception): pass

def check_dictatorship_unit(indict, path=[]):

    if len(path) >= 255:
        raise ExceptionDictatorshipUnitTooDeep("Dictatorship tree recursion limit reached `%(path)s'" % {
                'path': '/'.join(path)
                })

    # Supplied data defenetly must be a dict, othervice - error
    if not isinstance(indict, dict):
        raise ValueError("Supplied data is not a dict")

    # 'type' must be supplied
    if not 'type' in indict:
        raise ExceptionMissingDictatorshipUnitAttribute("Dictatorship unit type missing")

    # 'type' must be one of following
    if not indict['type'] in [
        'tag', 'dtd', 'comment', 'cdata', 'static',
        'pi', 'char'
        ]:
        raise ValueError("Wrong dictatorship unit type")

    # If 'type' is 'tag', then check 'tag_info' and everything,
    # what underlie
    if indict['type'] == 'tag':
        if not 'tag_info' in indict \
            or not isinstance(indict['tag_info'], dict):
            raise ExceptionMissingDictatorshipUnitAttribute(
                "Dictatorship unit type is `tag', but not `tag_info' supplied"
                )

        else:
            # tag name MUST be supplied and must be a string!
            if not 'name' in indict['tag_info']:
                raise ExceptionMissingDictatorshipUnitAttribute(
                    "`name' not supplied in dictatorship unit `tag_info'"
                    )
            else:
                if not isinstance(indict['tag_info']['name'], str):
                    raise TypeError("tag `name' must be a string")

            # attributes CAN be supplied or CAN be a None or a dict
            if 'attributes' in indict['tag_info']:
                if indict['tag_info']['attributes'] == None:
                    indict['tag_info']['attributes'] = {}
                else:
                    if not isinstance(indict['tag_info']['attributes'], dict):
                        raise TypeError("tag `attributes' must be dict")
                    else:
                        # attribute values can be a strings or callabels
                        for i in indict['tag_info']['attributes']:
                            if not isinstance(indict['tag_info']['attributes'][i], str):
                                raise TypeError("tag `attributes' dict values must be strings")
            else:
                indict['tag_info']['attributes'] = {}

            # 'tag_info' 'closed' attribute CAN be supplied and CAN be
            #  None or bool.
            if 'closed' in indict['tag_info']:
                if not isinstance(indict['tag_info']['closed'], bool):
                    raise TypeError("tag `closed' attribute can be only bool")
            else:
                indict['tag_info']['closed'] = False


            if 'placer' in indict['tag_info']:
                if not isinstance(indict['tag_info']['placer'], bool):
                    raise TypeError("wrong `placer' type")
            else:
                indict['tag_info']['placer'] = False


    for i in ['required_css', 'required_js']:
        if i in indict:
            if indict[i] == None:
                pass
            elif not isinstance(indict[i], list):
                raise TypeError("`%(i)s' can be list or None" % {
                    'i': i
                    })
            else:
                for j in indict[i]:
                    if not isinstance(indict[i][j], str):
                        raise TypeError("All `%(i)s' values must be strings" % {
                            'i': i
                            })

        else:
            indict[i] = None


    for i in ['module', 'uid']:
        if i in indict:
            if not re.match(r'[a-zA-Z][\w-]*', indict[i]):
                raise ValueError("Wrong `%(i)s' value at `%(path)s'" % {
                    'path': '/'.join(path),
                    'i': i
                    })
        else:
            raise ExceptionMissingDictatorshipUnitAttribute(
                "`%(i)s' required to be in unit!" % {
                    'i': i
                    }
                )

    if not 'content' in indict:
        indict['content'] = ''
    elif indict['content'] == None:
        indict['content'] = ''
    elif isinstance(indict['content'], str):
        pass
    elif isinstance(indict['content'], dict):
        pass
    else:
        raise ValueError("wrong unit content value")

    if indict['tag_info']['placer'] == True:
        if not isinstance(indict['content'], dict):
            raise ValueError("`placer' is True, so `content' MUST be dict")

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


    for i in [
        ('new_line_before_start', default_new_line_before_start),
        ('new_line_before_content', default_new_line_before_content),
        ('new_line_after_content', default_new_line_after_content),
        ('new_line_after_end', default_new_line_after_end)
        ]:
        if i[0] in indict:
            if not isinstance(indict[i[0]], bool):
                raise TypeError("-e- wrong `%(name)s' value type" % {
                    'name': i[0]
                    })
        else:
            indict[i[0]] = i[1]

    return




class XMLDictatorModulesDirError(Exception): pass


class XMLDictator:


    def __init__(self, xml_indent_size=2, generate_css=False, generate_js=False):

        # here linedup modules are listed. key is path
        self.units = {}

        # here will be stored
        self.tree_dict = {}

        # those four attributes are for code formatting
        # purposes
        self.xml_indent_size = xml_indent_size
        self.xml_indent = text.fill(' ', xml_indent_size)

        self.placer = None

        self.css_placeables = []
        self.js_placeables = []

        self.log = []

        self.log_size = 100

        self.generate_css = generate_css
        self.generate_js = generate_js

        return

    def do_log(self, text):

        log_l = len(self.log)

        if log_l >= self.log_size:
            self.log = self.log[-self.log_size:]

        self.log.append(text)


    def set_tree(self, indict):
        self.tree_dict = indict


    def _lineup_tree(self, indict, already_added, path=[]):

        ret = 0

        keys = list(indict.keys())
        keys.sort()

        if check_dictatorship_range(indict):

        for i in keys:

            if not id(indict[i]) in already_added:

                tmp = '/'.join(path + [i])

                if not tmp in self.units:
                    self.units[tmp] = indict[i]

                del(tmp)

                already_added.add(id(indict[i]))


            if isinstance(indict[i]['content'], dict):
                if self._lineup_tree(
                    indict[i]['content'], already_added, path=path + [i]
                    ) != 0:
                    self.do_log("-e- Inner tree lineup error error at `%(path)s'" % {
                        'path': '/'.join(path)
                        })
                    ret = 2

        return ret


    def lineup_tree(self):
        self.units = {}
        already_added = set()
        return self._lineup_tree(
            self.tree_dict, already_added, path=[]
            )


    def check_tree(self):
        ret = 0

        keys = list(self.units.keys())
        keys.sort()

        for i in keys:
            try:
                check_dictatorship_unit(self.units[i], i.split('/'))
            except:
                self.do_log("-e- Error while checking `%(path)s'\n%(exc_info)s" % {
                    'path': i,
                    'exc_info': error.return_exception_info(sys.exc_info())
                    })
                ret = 1

        return ret


    def find_placer(self):

        self.placer = None

        keys = list(self.units.keys())
        keys.sort()

        for i in keys:

            if 'tag_info' in self.units[i] \
                and 'placer' in self.units[i]['tag_info']:

                self.placer = self.units[i]
                break

        return


    def find_placeables(self):

        self.css_placeables = []
        self.js_placeables = []

        keys = list(self.units.keys())
        keys.sort()

        for i in keys:

            if not 'module' in self.units[i] \
                or not 'uid' in self.units[i]:
                continue


            if 'required_css' in self.units[i]:
                for j in self.units[i]['required_css']:
                    placeable_name = "%(module)s/%(uid)s/%(required)s" % {
                        'module': self.units[i]['module'],
                        'uid': self.units[i]['uid'],
                        'required': j,
                        }
                    if not placeable_name in self.css_placeables:
                        self.css_placeables.append()

            if 'required_js' in self.units[i]:
                for j in self.units[i]['required_js']:
                    placeable_name = "%(module)s/%(uid)s/%(required)s" % {
                        'module': self.units[i]['module'],
                        'uid': self.units[i]['uid'],
                        'required': j,
                        }
                    if not placeable_name in self.js_placeables:
                        self.js_placeables.append()

        return


    def css_path_renderer(self, inname):
        module, uid, file = inname.split('/')[0:2]

        return "/css?module=%(module)s&uid=%(uid)s&file=%(file)s" % {
            'module': urllib.parse.quote(module, encoding='utf-8', errors='strict'),
            'uid': urllib.parse.quote(uid, encoding='utf-8', errors='strict'),
            'file': urllib.parse.quote(file, encoding='utf-8', errors='strict')
            }


    def js_path_renderer(self, inname):
        module, uid = inname.split('/')[0:2]

        return "/js?module=%(module)s&uid=%(uid)s&file=%(file)s" % {
            'module': urllib.parse.quote(module, encoding='utf-8', errors='strict'),
            'uid': urllib.parse.quote(uid, encoding='utf-8', errors='strict'),
            'file': urllib.parse.quote(file, encoding='utf-8', errors='strict')
            }


    def place(self,
              css_path_renderer=css_path_renderer,
              js_path_renderer=js_path_renderer):



        last_placer_child_name = max(self.placer['content'])

        placement_i = 0

        for i in self.css_placeables:

            new_key = '%(last_placer_child_name)s-%(num)10d' % {
                'last_placer_child_name': last_placer_child_name,
                'num': placement_i
                }

            placement_i += 1

            self.placer['content'][new_key] = {
                'type': 'tag',
                'tag_info': {
                    'name': 'style',
                    'attributes': {
                        'type': 'text/css',
                        'src': css_path_renderer(i)
                        },
                    'closed': False
                    }
                }

        for i in self.js_placeables:

            new_key = '%(last_placer_child_name)s-%(num)10d' % {
                'last_placer_child_name': last_placer_child_name,
                'num': placement_i
                }

            placement_i += 1

            self.placer['content'][new_key] = {
                'type': 'tag',
                'tag_info': {
                    'name': 'script',
                    'attributes': {
                        'type': 'text/javascript',
                        'src': js_path_renderer(i)
                        },
                    'closed': False
                    }
                }

        return


    def _generate(self, root, indict, path=[]):

        ret = ''

        keys = list(indict.keys())
        keys.sort()

        inaddr_l = len(path)

        indent = text.fill(' ', inaddr_l * self.xml_indent_size)

        for i in keys:

            if 'uid' in indict[i]:
                self.uids[indict[i]['uid']] = indict[i]

            rendered = ''

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
                    attributes = self.generate_attributes(
                        indict[i]['tag_info']['attributes'], path,
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
                                root, indict[i]['content'], path=path + [i]
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

            ret += rendered

        return ret


    def generate(self):

        ret = 0

        if self.lineup_tree() != 0:
            self.do_log("-e- Some errors liningup dict tree")
            ret = 3

        if isinstance(ret, str):

            if self.check_tree() != 0:
                self.do_log("-e- Some dictatorship errors found")
                ret = 1

        if isinstance(ret, str):

            self.find_placer()
            if self.placer != None:
                self.find_placeables()
                self.place()


        if isinstance(ret, str):
            ret = self._generate(self.tree_dict, self.tree_dict, path=[])

        return ret

    def generate_attributes(self, indict, path=[], tagname=''):
        ret = ''

        inaddr_l = len(path)

        indent = text.fill(' ', inaddr_l * self.xml_indent_size)
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
            'uid': '4c890ca0-66fb-42ad-b519-d87811b695b3'
            },
        '010_xhtml_doctype': {
            'type': 'dtd',
            'content': 'html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"',
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
    b = XMLDictator()
    b.set_tree(a)
    ret = b.generate(True, True)

    return ret
