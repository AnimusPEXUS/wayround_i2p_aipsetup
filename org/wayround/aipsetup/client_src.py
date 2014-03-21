
import http.client
import json
import logging
import subprocess
import urllib.parse
import urllib.request


def list_(
    url,
    mask,
    searchmode='filemask',
    cs=True
    ):

    ret = None

    cst = 'off'
    if cs:
        cst = 'on'

    data = urllib.parse.urlencode(
        {
         'mask': mask,
         'searchmode': searchmode,
         'cs': cst,
         'action': 'search',
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    logging.debug("Data to send:\n{}".format(data))

    res = urllib.request.urlopen('{}list?{}'.format(url, data))

    if isinstance(res, http.client.HTTPResponse):
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def files(url, name):

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json',
         'name': name
         },
        encoding='utf-8'
        )

    logging.debug("Data to send:\n{}".format(data))

    res = urllib.request.urlopen('{}files?{}'.format(url, data))

    if isinstance(res, http.client.HTTPResponse):
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def get(url, path):

    p = subprocess.Popen(
        ['wget', '--no-check-certificate', '{}download{}'.format(url, path)]
        )

    ret = p.wait()

    return ret
