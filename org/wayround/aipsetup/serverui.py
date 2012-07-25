
import urllib

import org.wayround.utils.xml


#org.wayround.utils.xml.html()

def page_index():

    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True
        )

    a.set_tree(
        org.wayround.utils.xml.html(title="Unicorn distribution server",
             content={
                 'a': search()
                 }
             )
        )

    txt = a.render()

    return txt

def page_search_results(results, which):

    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True
        )

    a.set_tree(
        org.wayround.utils.xml.html(title="Search Results",
             content={
                 'a': search_results(results, which)
                 }
             )
        )

    txt = a.render()

    return txt

def page_infolist(lst):
    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True
        )

    a.set_tree(
        org.wayround.utils.xml.html(title="Search Results",
             content={
                 'a': infolist(lst)
                 }
             )
        )

    txt = a.render()

    return txt




def search_test():
    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True
        )
    a.set_tree(org.wayround.utils.xml.html(content={'a': search() }))
    txt = a.render()
    print(txt)

def search():
    module = 'search'
    return org.wayround.utils.xml.tag(
        'div',
        module=module,
        uid='search-root-div',
        required_css=['search.css'],
        content={
            'form': org.wayround.utils.xml.tag(
                'form',
                attributes={'action': 'search'},
                content={
                    'table': org.wayround.utils.xml.tag(
                        'table',
                        content={
                            'tr0': org.wayround.utils.xml.tag(
                                'tr',
                                content={
                                    'td0': org.wayround.utils.xml.tag(
                                        'td',
                                        content="Search For What?"
                                        ),
                                    'td1': org.wayround.utils.xml.tag(
                                        'td',
                                        content={
                                            'select': org.wayround.utils.xml.tag(
                                                'select',
                                                attributes={'name':'what'},
                                                content={
                                                    'option1': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'info'},
                                                        content='info'
                                                        ),
                                                    'option2': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'source'},
                                                        content='source'
                                                        ),
                                                    'option3': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={
                                                            'value': 'repository',
                                                            'selected': 'selected'
                                                            },
                                                        content='repository'
                                                        )
                                                    }
                                                )
                                            }
                                        )
                                    }
                                ),
                            'tr1': org.wayround.utils.xml.tag(
                                'tr',
                                content={
                                    'td0': org.wayround.utils.xml.tag(
                                        'td',
                                        content="How to search?"
                                        ),
                                    'td1': org.wayround.utils.xml.tag(
                                        'td',
                                        content={
                                            'select': org.wayround.utils.xml.tag(
                                                'select',
                                                attributes={'name':'how'},
                                                content={
                                                    'option1': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'regexp'},
                                                        content='regexp'
                                                        ),
                                                    'option2': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'begins'},
                                                        content='begins'
                                                        ),
                                                    'option3': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'exac'},
                                                        content='exac'
                                                        ),
                                                    'option4': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'contains'},
                                                        content='contains'
                                                        )
                                                    }
                                                )
                                            }
                                        )
                                    }
                                ),
                            'tr2': org.wayround.utils.xml.tag(
                                'tr',
                                content={
                                    'td0': org.wayround.utils.xml.tag(
                                        'td',
                                        content="View"
                                        ),
                                    'td1': org.wayround.utils.xml.tag(
                                        'td',
                                        content={
                                            'select': org.wayround.utils.xml.tag(
                                                'select',
                                                attributes={'name':'view'},
                                                content={
                                                    'option1': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'html', 'selected':'selected'},
                                                        content='html'
                                                        ),
                                                    'option2': org.wayround.utils.xml.tag(
                                                        'option',
                                                        attributes={'value': 'list'},
                                                        content='list'
                                                        )
                                                    }
                                                )
                                            }
                                        )
                                    }
                                ),
                            'tr3': org.wayround.utils.xml.tag(
                                'tr',
                                content={
                                    'td0': org.wayround.utils.xml.tag(
                                        'td',
                                        content="Case Sensitive"
                                        ),
                                    'td1': org.wayround.utils.xml.tag(
                                        'td',
                                        content={
                                            'input': org.wayround.utils.xml.tag(
                                                'input',
                                                closed=True,
                                                attributes={
                                                    'type': 'checkbox',
                                                    'name': 'sensitive'
                                                    }
                                                )
                                            }
                                        )
                                    }
                                ),
                            'tr4': org.wayround.utils.xml.tag(
                                'tr',
                                content={
                                    'td0': org.wayround.utils.xml.tag(
                                        'td',
                                        content="Query"
                                        ),
                                    'td1': org.wayround.utils.xml.tag(
                                        'td',
                                        content={
                                            'input': org.wayround.utils.xml.tag(
                                                'input',
                                                closed=True,
                                                attributes={
                                                    'type': 'text',
                                                    'name': 'value'
                                                    }
                                                )
                                            }
                                        )
                                    }
                                ),
                            'tr5': org.wayround.utils.xml.tag(
                                'tr',
                                content={
                                    'td0': org.wayround.utils.xml.tag(
                                        'td',
                                        content=""
                                        ),
                                    'td1': org.wayround.utils.xml.tag(
                                        'td',
                                        content={
                                            'button': org.wayround.utils.xml.tag(
                                                'button',
                                                closed=False,
                                                attributes={
                                                        'type': 'submit'
                                                    },
                                                content='Go!'
                                                )
                                            }
                                        )
                                    }
                                )
                            }
                        )
                    }
                )
            }
        )

def control():
    return org.wayround.utils.xml.tag(
        'div',
        content={
            'form1': org.wayround.utils.xml.tag(
                'form',
                attributes={
                    'action': 'control'
                    },
                content={
                    'button': org.wayround.utils.xml.tag(
                        'button',
                        attributes={
                            'type': 'submit',
                            'name': 'action',
                            'value': 'reload'
                            },
                        content="Reload Indexes"
                        )
                    }
                ),
            'form2': org.wayround.utils.xml.tag(
                'form',
                attributes={
                    'action': 'control'
                    },
                content={
                    'button': org.wayround.utils.xml.tag(
                        'button',
                        attributes={
                            'type': 'submit',
                            'name': 'action',
                            'value': 'reindex'
                            },
                        content="Reindex Sources And Repository, after what Reload Indexes"
                        )
                    }
                )
            }
        )


def info_card(
    name,
    pkg_name_type,
    regexp,
    buildinfo,
    description,
    homepage,
    category,
    tags
    ):

    return org.wayround.utils.xml.tag(
        'div',
        module='info',
        uid='card',
        content={
            '01_header': org.wayround.utils.xml.tag(
                'h2',
                content=name
                ),
            '02_link': org.wayround.utils.xml.tag(
                'em',
                content={
                    '1_(': org.wayround.utils.xml.char('('),
                    '2_a': org.wayround.utils.xml.tag(
                        'a',
                        attributes={
                            'href': 'files_info/{}'.format(name)
                            },
                        content='xml'
                        ),
                    '3_)': org.wayround.utils.xml.char(')')
                    }
                ),
            '03_table': org.wayround.utils.xml.tag(
                'table',
                content={
                    'tr_01': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='File Name Type'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content=pkg_name_type
                                )
                            }
                        ),
                    'tr_02': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='Regular Expression'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content={
                                    'pre': org.wayround.utils.xml.tag(
                                        'pre',
                                        content=regexp
                                        )
                                    }
                                )
                            }
                        ),
                    'tr_03': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='Builder'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content=buildinfo
                                )
                            }
                        ),
                    'tr_04': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='Description'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content={
                                    'pre': org.wayround.utils.xml.tag(
                                        'pre',
                                        content=description
                                        )
                                    }
                                )
                            }
                        ),
                    'tr_05': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='Home Page'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content={
                                    'a': org.wayround.utils.xml.tag(
                                        'a',
                                        attributes={
                                            'hreaf': homepage
                                            },
                                        content=homepage
                                        )
                                    }
                                )
                            }
                        ),
                    'tr_06': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='Category'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content=category
                                )
                            }
                        ),
                    'tr_07': org.wayround.utils.xml.tag(
                        'tr',
                        content={
                            'td_0': org.wayround.utils.xml.tag(
                                'td',
                                content='Tags'
                                ),
                            'td_1': org.wayround.utils.xml.tag(
                                'td',
                                content=', '.join(tags)
                                )
                            }
                        )
                    }
                )
            }
        )

def search_results(results, which):

    if not which in ['source', 'repository', 'info']:
        raise ValueError("Wrong `which' value")

    count = len(results)
    length = len(str(count))

    res_dict = {}

    if which in ['source', 'repository']:
        for i in range(count):
            res_dict[('{:#0' + str(length) + '}').format(i)] = org.wayround.utils.xml.tag(
                'a',
                attributes={
                    'href': 'files_{}'.format(results[i])
                    },
                content=results[i]
                )
    elif which == 'info':
        for i in range(count):
            res_dict[('{:#0' + str(length) + '}').format(i)] = org.wayround.utils.xml.tag(
                'a',
                attributes={
                    'href': 'info?name={}'.format(urllib.parse.quote(str(results[i])))
                    },
                content=results[i]
                )
    else:
        res_dict = None


    ret = org.wayround.utils.xml.tag(
        'div',
        content={
            '001_count_div': org.wayround.utils.xml.tag(
                'div',
                content={
                    '01_caption': org.wayround.utils.xml.char('Count: '),
                    '02_strong': org.wayround.utils.xml.tag(
                        'strong',
                        content=str(len(results))
                        )
                    }
                ),
            '002_results_div': org.wayround.utils.xml.tag(
                'div',
                content=res_dict
                )
            }
        )

    return ret


def infolist(lst):

    lst_c = len(lst)
    lst_l = len(str(lst_c))

    toc_sl = []
    cc = ''
    for i in lst:
        if cc != i[0]:
            toc_sl.append(i[0])
            cc = i[0]

    toc_sl.sort()
    toc_sl_c = len(toc_sl)
    toc_sl_l = len(str(toc_sl_c))

    lst.sort()


    toc = {}
    for i in range(toc_sl_c):
        toc[('{:#0' + str(toc_sl_l) + '}').format(i)] = org.wayround.utils.xml.tag(
            'a',
            attributes={
                'href': '#{}'.format(urllib.parse.quote(toc_sl[i]))
                },
            content=toc_sl[i]
            )

    infolist_letter = {}

    for i in range(toc_sl_c):

        infos = {}

        for j in lst:
            if j[0] == toc_sl[i]:
                infos[('{:#0' + str(lst_l) + '}').format(j)] = org.wayround.utils.xml.tag(
                    'div',
                    content={
                        'a': org.wayround.utils.xml.tag(
                            'a',
                            attribute={
                                'href': "info?name={}".format(j)
                                },
                            content=j
                            )
                        }
                    )

        infolist_letter[('{:#0' + str(toc_sl_l) + '}').format(i)] = org.wayround.utils.xml.tag(
            'div',
            # class infolist-letter
            content={
                '01_h2': org.wayround.utils.xml.tag(
                    'h2',
                    attributes={
                        'id': toc_sl[i]
                        },
                    content=toc_sl[i]
                    ),
                '02_div': org.wayround.utils.xml.tag(
                    'div',
                    content=infos
                    )
                }
            )

    info_list = org.wayround.utils.xml.tag(
        'div',
        content={
            '001_toc': org.wayround.utils.xml.tag(
                'div',
                content=toc
                )
            }
        )

    return info_list
