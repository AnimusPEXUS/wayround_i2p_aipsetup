

import name


def version_comparator(name1, name2, nametype, action, limit):

    ret = 0

    d2 = ''
    
    d1 = name.source_name_parse(name1, nametype)
    d2 = name.source_name_parse(name2, nametype)

    if nametype == 'standard':
        pass
    
    return ret


def standard_comparison(e1, e2):

    vers1 = e1.split('.')
    vers2 = e2.split('.')

    longer = None

    v1l = len(vers1)
    v2l = len(vers2)

    #  length used in first comparison part
    el_1 = v1l

    if v1l == v2l:
        longer = None
        el_1 = v1l

    elif v1l > v2l:
        longer = 'vers1'
        el_1 = v2l

    else:
        longer = 'vers2'
        el_1 = v1l

    # first comparison part

    for i in range(el_1):
        if vers1[i] > vers2[i]:
            return +1
        elif vers1[i] < vers2[i]:
            return -1
        else:
            continue

    # second comparison part

    if longer != None:
        if longer == 'vers1':
            return +1
        else:
            return -1


    return 0
