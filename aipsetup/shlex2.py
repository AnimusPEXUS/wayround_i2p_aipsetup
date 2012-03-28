#!/usr/bin/python2.6

def split(str_line):

    params = []

    str_line = str_line.strip()
    str_line_len=len(str_line)

    i = 0
    cur = 0

    if str_line_len > 0:
        while True:

            if i == str_line_len:
                params += work_param(str_line[cur:i+1])
                break
            elif str_line[i] == ' ':
                if i > 0 and str_line[i-1] == '\\':
                    i += 1
                    continue
                
                params += work_param(str_line[cur:i])
                cur = i
                while True:
                    if i == str_line_len:
                        break
                    if str_line[i] != ' ':
                        cur = i
                        break
                    i += 1
                continue
            elif str_line[i] in ['"', "'"]:
                if i > 0 and str_line[i-1] == '\\':
                    i += 1
                    continue
                qc = str_line[i]
                i += 1

                if i == str_line_len:
                    continue

                p = find_quot(str_line, qc, i)
                if p == None:
                    i = str_line_len
                    continue
                i = p

                if i == str_line_len:
                    continue

                i += 1
                continue
            else:
                i += 1

    return params

def work_param(str_line):
    ret = correct_quotes_remove(str_line)
    ret = unquote_chars(ret)
    return [ret]


def correct_quotes_remove(str_line):
    ret = str_line

    q0 = None
    q1 = None
    cut0 = []
    cut1 = []
    cut2 = []

    for c in ['"', "'"]:
        while True:
            ret_len=len(ret)

            cut0 = [0]
            q0 = find_chars(ret, start=0, chars=c)

            if q0[0] == None:
                break

            cut0.append(q0[1])

            cut1=[cut0[1]+1]

            q1 = find_chars(ret, start=cut1[0], chars=c)

            if q1[0] == None:
                break

            cut1.append(q1[1])

            cut2 = [q1[1]+1, ret_len]

            ret = ret[cut0[0]:cut0[1]] + ret[cut1[0]:cut1[1]] + ret[cut2[0]:cut2[1]]

    return ret

def unquote_chars(str_line, chars=" '\""):
    clst = []
    for c in chars:
        clst.append(c)
    clst = list(set(clst))
    clst.sort()

    for c in clst:
        str_line.replace('\\'+c, c)

    return str_line

def find_chars(str_line, start=0, chars=" '\""):

    clst = []
    for c in chars:
        clst.append(c)
    clst = list(set(clst))
    clst.sort()
    lst = []

    for c in clst:
        cp = str_line.find(c, start)
        if cp != -1:
            if cp == 0 or (str_line[cp-1] != '\\'):
                lst.append([c, cp])

    ret = None
    l_lst = len(lst)

    if l_lst == 0:
        ret = (None, None)
    elif l_lst == 1:
        ret = tuple(lst[0])
    else:
        ret = tuple(lst[0])

        for e in lst:
            if e[1] < ret[1]:
                ret = tuple(e)

    return ret

def find_quot(str_line, qc, start):

    ret = None

    cp = str_line.find(qc, start)
    if cp != -1:
        if cp == 0 or (str_line[cp-1] != '\\'):
            ret = cp

    return ret
