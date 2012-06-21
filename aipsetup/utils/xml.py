
import copy
import xml.sax.saxutils

from . import file
from . import text



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
            if indict['type'] == 'tag' and not 'tag_info' in indict:
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
                            ret = 0
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

                # 'tag_info' 'closed' attribute CAN be supplied and CAN be
                #  None or bool.
                if ret == 0:
                    if 'closed' in indict['tag_info']:
                        if not isinstance(indict['tag_info']['closed'], bool):
                            if debug:
                                print("-e- tag `closed' attribute can be only bool")
                            ret = 13

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

                        # 'css' can have 'separate' attribute which
                        # must be bool
                        if ret == 0:
                            if 'separate' in indict['tag_info']['css']:
                                if not isinstance(indict['tag_info']['css']['separate'], bool):
                                    if debug:
                                        print("-e- wrong `scc' `separate' value type")
                                    ret = 19
                            else:
                                indict['tag_info']['css']['separate'] = True

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
                for i in ['new_line_before_start',
                    'new_line_before_content',
                    'new_line_after_content',
                    'new_line_after_end'
                    ]:

                    if i in indict:
                        if not isinstance(indict[i], bool):
                            if debug:
                                print("-e- wrong `%(name)s' value type" % {
                                    'name': i
                                    })
                            ret = 23
                            break
                    else:
                        indict[i] = False


        if ret == 0:
            if 'cache' in indict \
                and indict['cache'] != None \
                and not isinstance(indict['cache'], bool):
                    if debug:
                        print("-e- wrong cache value")
                    ret = 5

        if ret == 0:
            if not 'content' in indict:
                if debug:
                    print("-e- unit `content' missing")
                ret = 6
            elif indict['content'] == None:
                ret = 0
            elif isinstance(indict['content'], (str, dict)):
                ret = 0
            elif callable(indict['content']):
                ret = 0
            else:
                if debug:
                    print("-e- wrong unit content value")
                ret = 7

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

def generate_attributes(indict, args=[], kvargs={}, debug=False, indaddr=[]):
    ret = ''

    for i in list(indict.keys()):

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
                ret += '%(name)s="%(value)s"' % {
                    'name': i,
                    'value': xml.sax.saxutils.escape(value)
                    }
            except:
                ret = 1
                break

    return ret


class XMLDictator:

    def __init__(self,
                 static_files_dir,
                 css_cache_dir,
                 xml_cache_dir):

        for i in [static_files_dir,
                  css_cache_dir,
                  xml_cache_dir]:

            if file.create_if_not_exists_dir(i) != 0:
                raise Exception

        self.xml_files = {}
        self.css_files = {}

    def _generate(self, indict, args=[], kvargs={}, debug=False, indaddr=[]):
        ret = ''

        keys = list(indict.keys())
        keys.sort()

        inaddr_l = len(indaddr)

        for i in keys:

            new_line_before_start = ''
            if indict['new_line_before_start']:
                new_line_before_start = '\n'

            new_line_before_content = ''
            if indict['new_line_before_content']:
                new_line_before_content = '\n'

            new_line_after_content = ''
            if indict['new_line_after_content']:
                new_line_after_content = '\n'


            new_line_after_end = ''
            if indict['type'] == 'comment':
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
                end = ' -->'

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

                if indict[i]['tag_info']['attributes'] != None:
                    attributes = generate_attributes()

                    if not isinstance(attributes, str):
                        ret = 1

                if isinstance(ret, str):

                    closing_slash = ''
                    if indict[i]['tag_info']['closed']:
                        closing_slash = '/'

                    start = '<%(tagname)s %(attributes)s %(closing_slash)s>' % {
                        'tagname': indict[i]['tag_info']['name'],
                        'attributes': attributes,
                        'closing_slash': closing_slash
                        }

                    if not indict[i]['tag_info']['closed']:
                        content = indict[i]['content']
                        end = ''
                    else:
                        content = ''
                        end = ''

            else:
                raise ValueError


            text = ("" \
                + "%(new_line_before_start)s" \
                + "%(start)s" \
                + "%(new_line_before_content)s" \
                + "%(content)s" \
                + "%(new_line_after_content)s" \
                + "%(end)s" \
                + "%(new_line_after_end)s") % {
                'new_line_before_start': new_line_before_start,
                'new_line_before_content': new_line_before_content,
                'new_line_after_content': new_line_after_content,
                'new_line_after_end': new_line_after_end,
                'start': start,
                'content': content,
                'end': end
                }


            #if indict[i]['type'] == 'tag':
                #if isinstance(indict[i]['contents'], dict):
                    #if self._generate(
                        #indict[i]['contents'],
                        #debug=debug,
                        #indaddr=copy.copy(indaddr) + [i]
                        #) != 0:
                        #ret = 2
                        #break

        return ret

    def generate(self, indict, args=[], kvargs={}, debug=False):

        ret = 0

        if dictatorship_tree_check(indict, debug) != 0:
            if debug:
                print("-e- Some dictatorship errors found")
            ret = 1
        else:
            ret = self._generate(indict, args, kvargs, debug, indaddr=[])

        return ret

def test():
    # Upper dict element with names (like folloving) is called
    # `dictatorship range'.
    # Dictatorship range's keys must point only on dict-s,
    # othervice it is an error.
    a = {
        '100_html_tag': {
            # Dictatorship gange pointet dicts (like this)
            # is called `dictatorship unit'

            # Any dict can be one of folloving types:
            # 'tag', 'dtd', 'comment', 'cdata', 'static', 
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
            'new_line_before_start': False,
            'new_line_before_content': False,
            'new_line_after_content': False,
            'new_line_after_end': False,

            # 'tag_info' required to present if type is 'tag'.
            # 'tag_info' must be a dict.
            'tag_info': {
                # any valid tag name
                'name': 'html',

                # None or dict
                # dict values can be strings or
                # callables returning strings
                'attributes': None,

                # (bool) if True - no contents is
                # passible and any info supplied in 'contents'
                # will be omited. Default is False.
                'closed': False,

                # None or dict
                'css': {
                        # None, 'static', 'dynamic' or 'inline'
                        # if 'static', uuid-named file
                        # from 'static_css' dir will be
                        # used;
                        # if 'dynamic', css will be
                        # generated from underlying
                        # "tags"
                        # If type is None, benerator behaves
                        # like if css is None. This can be used
                        # as a fast switch.
                        # If type is 'inline', then tag's `style'
                        # attribute is used
                        'type': 'dynamic',

                        # 'contents' must present if 'type' is 'static'.
                        # 'contents' can be None, string or callable
                        'contents': None,

                        # If this setting exists and is True,
                        # then from this point and to the new point,
                        # separate CSS is generated, ientified by
                        # uuid. Default is True
                        'separate': True,

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
            'cache': False,

            # str, dict, None, callable
            # None - exchenged to empty string
            # string - used as is
            # dict - assumed tobe new
            # `dictatorship range'
            # callable - must return string
            'content': ''

            }
        }

    dtc = dictatorship_tree_check(a, True)
    if dtc != 0:
        print("DTC test error: %(num)d" % {
            'num': dtc
            })
    else:
        print("Dictator test")
        b = XMLDictator(static_files_dir='/mnt/sda3/home/agu/p/aipsetup/tests/static',
                        css_cache_dir='/mnt/sda3/home/agu/p/aipsetup/tests/css-c',
                        xml_cache_dir='/mnt/sda3/home/agu/p/aipsetup/tests/xml-c')
        ret = b.generate(a, [], {}, True)

    return ret
