
import copy
import os.path
import sys
import xml.sax.saxutils


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

def check_dictatorship_unit(indict, debug=False):

    ret = 0

    # Supplied data defenetly must be a dict, othervice - error
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
                                        if not isinstance(indict['tag_info']['attributes'][i], str) \
                                            and not callable(indict['tag_info']['attributes'][i]):
                                            if debug:
                                                print("-e- tag `attributes' dict values must be strings or callcables")
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

                    # Process 'css', which CAN be, and if it is, then it
                    # MUST be a dict or None
                    if ret == 0:
                        if not 'css' in indict['tag_info']:
                            ret = 0
                        elif indict['tag_info']['css'] == None:
                            ret = 0
                        elif not isinstance(indict['tag_info']['css'], dict):
                            if debug:
                                print("-e- wrong tag `css' attribute")
                            ret = 14
                        else:
                            # 'css' MUST have a 'type'
                            if not 'type' in indict['tag_info']['css']:
                                if debug:
                                    print("-e- wrong tag `css' must have `type' attribute")
                                ret = 15
                            else:
                                # 'css' 'type' can be None
                                if indict['tag_info']['css']['type'] == None:
                                    ret = 0
                                else:

                                    # 'css' 'type' can be on of folloving
                                    if not indict['tag_info']['css']['type'] in ['static', 'dynamic', 'inline']:
                                        if debug:
                                            print("-e- wrong tag `css' `type' value")
                                        ret = 16
                                    else:
                                        # if 'css' 'type' is 'static', then it MUST be supplied
                                        # by 'css' 'contents'
                                        if indict['tag_info']['css']['type'] == 'static':
                                            if not 'contents' in indict['tag_info']['css']:
                                                if debug:
                                                    print("-e- `scc' `contents' must be supplied if `css' `type' is `static'")
                                                ret = 17
                                            else:
                                                if indict['tag_info']['css']['contents'] == None:
                                                    ret = 0
                                                elif isinstance(indict['tag_info']['css']['contents'], str):
                                                    ret = 0
                                                elif callable(indict['tag_info']['css']['contents']):
                                                    ret = 0
                                                else:
                                                    if debug:
                                                        print("-e- wrong `scc' `contents' value type")
                                                    ret = 18

                            # 'css' can have 'cache' attribute which
                            # must be bool
                            if ret == 0:
                                if 'cache' in indict['tag_info']['css']:
                                    if not isinstance(indict['tag_info']['css']['cache'], bool):
                                        if debug:
                                            print("-e- wrong `cache' `separate' value type")
                                        ret = 20
                                else:
                                    indict['tag_info']['css']['cache'] = False

                            if ret == 0:
                                if 'style' in indict['tag_info']['css']:
                                    if indict['tag_info']['css']['style'] == None:
                                        ret = 0
                                    elif not isinstance(indict['tag_info']['css']['style'], dict):
                                        if debug:
                                            print("-e- `css' `style' attribute must be a dict")
                                        ret = 21
                                    else:
                                        for i in indict['tag_info']['css']['style']:
                                            for j in indict['tag_info']['css']['style'][i]:
                                                if isinstance(indict['tag_info']['css']['style'][i][j], str):
                                                    ret = 0
                                                elif callable(indict['tag_info']['css']['style'][i][j]):
                                                    ret = 0
                                                else:
                                                    if debug:
                                                        print("-e- wrong style value")

                                                    ret = 22
                                                    break

                                            if ret != 0:
                                                break

        if ret == 0:
            if 'cache' in indict:
                if not isinstance(indict['cache'], bool):
                    if debug:
                        print("-e- wrong cache value")
                    ret = 5
            else:
                indict['cache'] = False

        if ret == 0:
            if indict['cache'] and not 'uuid' in indict:
                if debug:
                    print("-e- cache requested, but not uuid defined")
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
            elif callable(indict['content']):
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

def _check_dictatorship_range(indict, debug=False, address=[]):

    ret = 0

    if check_dictatorship_range(indict, debug) != 0:
        if debug:
            print("-e- Range error at `%(path)s'" % {
                'path': '/'.join(address)
                })
        ret = 1
    else:

        keys = list(indict.keys())
        keys.sort()

        for i in keys:
            if check_dictatorship_unit(indict[i], debug) != 0:
                if debug:
                    print("-e- Unit error at `%(path)s'" % {
                        'path': '/'.join(address)
                        })
                ret = 2
                break
            else:
                if indict[i]['type'] == 'tag':
                    if isinstance(indict[i]['content'], dict):
                        if _check_dictatorship_range(
                            indict[i]['content'],
                            debug=debug,
                            address=copy.copy(address) + [i]
                            ) != 0:
                            ret = 3
                            break

    return ret

def dictatorship_tree_check(indict, debug=False):
    return _check_dictatorship_range(indict, debug, address=[])

def generate_attributes(indict, args=[], kvargs={}, debug=False, indaddr=[],
                        indent_size=2, tagname=''):
    ret = ''

    inaddr_l = len(indaddr)

    indent = text.fill(' ', inaddr_l * indent_size)
    nameindent = text.fill(' ', len(tagname))

    attrs = []
    keys = list(indict.keys())
    keys.sort()
    for i in keys:

        if ret != '':
            ret += ' ';

        value = ''
        if callable(indict[i]):
            try:
                value = indict[i](indict, args=[], kvargs={}, debug=False,
                                  indaddr=indict)
            except:
                ret = 1
        elif isinstance(indict[i], str):
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



class XMLDictator:


    def __init__(self,
                 css_static_dir,
                 css_cache_dir,
                 xml_cache_dir):

        self.css_static_dir = css_static_dir
        self.css_cache_dir = css_cache_dir
        self.xml_cache_dir = xml_cache_dir

        self.uuids = {}

        for i in [css_static_dir,
                  css_cache_dir,
                  xml_cache_dir]:

            if file.create_if_not_exists_dir(i) != 0:
                raise Exception



        #        self.xml_files = {}
        #        self.css_files = {}


    def generate_css_from_dict(self, indict, uuid, pseudo,
                               cache=False, typ='dinamic',
                               mode='block', debug=False):

        if not typ in ['static', 'dynamic']:
            raise ValueError

        if not mode in ['block', 'inline']:
            raise ValueError

        ret = 0

        if mode == 'inline':
            pseudo = 'inline'

        if pseudo == '':
            pseudo = 'default'

        uuid_mode_pseudo_css_filename = 'uuid-%(uuid)s.%(mode)s.%(pseudo)s.css' % {
            'uuid': uuid,
            'mode': mode,
            'pseudo': pseudo
            }

        css_cache_file_name = os.path.join(
            self.css_cache_dir,
            uuid_mode_pseudo_css_filename
            )

        css_static_file_name = os.path.join(
            self.css_static_dir,
            uuid_mode_pseudo_css_filename
            )


        if typ == 'static':


        if cache and os.path.exists(css_cache_file_name):
            try:
                f = open(css_cache_file_name, 'r')
                rendered = f.read()
                f.close()
            except:
                if debug:
                    print("-e- Can't load cache XML file `%(name)s'" % {
                        'name': css_cache_file_name
                        })
                    error.print_exception_info(sys.exc_info())
                ret = 2
                break

        css_txt = ''

        if mode == 'block':

            keys = list(indict.keys())
            keys.sort()

            css_txt = '.css-%(uuid)s {\n' % {
                'uuid': uuid
                }

            for i in keys:
                css_txt += '%(indent)s%(property)s: %(value)s;\n' % {
                    'indent': '    ',
                    'property': i,
                    'value': indict[i]
                    }

            css_txt += '}\n'

        elif typ == '':
            css_txt = ''

            for i in keys:
                css_txt += '%(property)s: %(value)s;' % {
                    'property': i,
                    'value': indict[i]
                    }

        else:
            # else is only for sake of complitteness :-) 
            pass


    def _generate(self, root, indict,
                  args=[], kvargs={},
                  debug=False, indaddr=[],
                  indent_size=2, current_css_uuid=None):

        ret = ''

        keys = list(indict.keys())
        keys.sort()

        inaddr_l = len(indaddr)

        indent = text.fill(' ', inaddr_l * indent_size)

        for i in keys:

            if 'uuid' in indict[i]:
                self.uuids[indict[i]['uuid']] = indict[i]

            if indict[i]['cache']:
                xml_cache_file_name = os.path.join(
                    self.xml_cache_dir,
                    indict[i]['uuid'] + '.xml'
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
                    if callable(indict[i]['content']):
                        content = indict[i]['content'](
                            indict, args=[], kvargs={}, debug=False, indaddr=[]
                            )
                    elif isinstance(indict[i]['content'], str):
                        content = indict[i]['content']

                    # NOTE: May be next line need to be reworked
                    content = content.replace('--', '-')

                    end = ' -->'

                elif indict[i]['type'] == 'pi':
                    start = '<?'
                    if callable(indict[i]['content']):
                        content = indict[i]['content'](
                            indict, args=[], kvargs={}, debug=False, indaddr=[]
                            )
                    elif isinstance(indict[i]['content'], str):
                        content = indict[i]['content']
                    end = '?>'

                elif indict[i]['type'] == 'dtd':
                    start = '<!DOCTYPE '
                    if callable(indict[i]['content']):
                        content = indict[i]['content'](
                            indict, args=[], kvargs={}, debug=False, indaddr=[]
                            )
                    elif isinstance(indict[i]['content'], str):
                        content = indict[i]['content']
                    end = '>'

                elif indict[i]['type'] == 'cdata':
                    start = '<![CDATA['
                    # NOTE: May be next line need to be reworked
                    content = indict[i]['content'].replace(']]>', '')
                    end = ']]>'

                elif indict[i]['type'] == 'char':
                    start = ''
                    if callable(indict[i]['content']):
                        content = indict[i]['content'](
                            indict, args=[], kvargs={}, debug=False, indaddr=[]
                            )
                    elif isinstance(indict[i]['content'], str):
                        content = indict[i]['content']
                    content = xml.sax.saxutils.escape(content)
                    end = ''

                elif indict[i]['type'] == 'static':
                    start = ''
                    content = indict[i]['content']
                    end = ''

                elif indict[i]['type'] == 'tag':

                    css_uuid = current_css_uuid

                    if 'css' in indict[i] \
                        and isinstance(indict[i]['css'], dict) \
                        and indict[i]['css']['type'] != None:
                            if indict[i]['css']['separate']:
                                # TODO: ensure uuid existance 
                                css_uuid = indict[i]['uuid']



                    attributes = ''
                    if indict[i]['tag_info']['attributes'] != None:
                        attributes = generate_attributes(
                            indict[i]['tag_info']['attributes'], args,
                            kvargs, debug, indaddr,
                            tagname=indict[i]['tag_info']['name']
                            )

                        if not isinstance(attributes, str):
                            ret = 1

                    if 'uuid' in indict[i]:
                        indict[i]['tag_info']['attributes']['class'] += ' .uuid-%(uuid)s' % {
                            'uuid': indict[i]['uuid']
                            }

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
                            c = None
                            if callable(indict[i]['content']):
                                c = indict[i]['content'](args, kvargs, debug)
                            else:
                                c = indict[i]['content']

                            if isinstance(c, str):
                                content = c
                            elif isinstance(c, dict):
                                content = self._generate(
                                    root, c, args, kvargs, debug, indaddr=indaddr + [i],
                                    indent_size=indent_size,
                                    current_css_uuid=current_css_uuid
                                    )
                            else:
                                content = str(c)

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

    def generate(self, indict, args=[], kvargs={}, debug=False,
                 indent_size=2):

        ret = 0

        if dictatorship_tree_check(indict, debug) != 0:
            if debug:
                print("-e- Some dictatorship errors found")
            ret = 1
        else:
            ret = self._generate(
                indict, indict, args, kvargs, debug,
                indaddr=[],
                indent_size=indent_size,
                current_css_uuid=None
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
            'uuid': '4c890ca0-66fb-42ad-b519-d87811b695b3'
            },
        '010_xhtml_doctype': {
            'type': 'dtd',
            'content': 'html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"',
            'cache': True,
            'uuid': 'e156ce9f-eaf4-4f24-96ca-594b3af0944b'
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
            # The uuid is not required in every dict.
            # If uuid is used by css, then "uuid-%(uuid)s" class
            # will be added to the tag.
            'uuid': '55aeee15-ba79-4e78-a848-2c65c2e0d6a0',

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
                # dict values can be strings or
                # callables returning strings
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
                'closed': False,

                # None or dict
                'css': {
                        # None, 'static', 'dynamic'
                        # if 'static', uuid-named file
                        # from 'static_css' dir will be
                        # used;
                        # if 'dynamic', css will be
                        # generated from underlying
                        # "tags"
                        # If type is None, benerator behaves
                        # like if css is None. This can be used
                        # as a fast switch.
                        'type': 'dynamic',

                        # 'block' or 'inline'.
                        # if 'inline', only '' style is used
                        'mode': 'block',

                        # 'contents' must present if 'type' is 'static'.
                        # 'contents' can be None, string or callable
                        'contents': None,

                        # is will be generated evey time or cache will
                        # be used, Default is False
                        'cache': True,

                        # styles to apply.
                        'styles': {
                            '': {
                                    # value can be string or callable
                                    'border': '1px black solid'
                                },
                            'hover': {
                                }
                            # etc.
                            }
                    }
                },

            # None or bool. if is bool, then 'uuid' is required
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
                        'name': 'head'
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
                        }
                    }
                }

            }
        }

    dtc = dictatorship_tree_check(a, True)
    if dtc != 0:
        print("DTC test error: %(num)d" % {
            'num': dtc
            })
        ret = 1
    else:
        print("Dictator test")
        b = XMLDictator(static_files_dir='/mnt/sda3/home/agu/p/aipsetup/tests/static',
                        css_cache_dir='/mnt/sda3/home/agu/p/aipsetup/tests/css-c',
                        xml_cache_dir='/mnt/sda3/home/agu/p/aipsetup/tests/xml-c')
        ret = b.generate(a, [], {}, True)

    return ret
