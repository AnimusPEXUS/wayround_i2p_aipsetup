
import http.client
import json
import logging
import subprocess
import urllib.parse
import urllib.request


class SourceServerClient:

    def __init__(self, url):
        self._url = url
        return

    def search(self, mask, searchmode='filemask', cs=True):
        return search(self._url, mask, searchmode, cs)

    def files(self, name):
        return files(self._url, name)

    def get(self, path, wd='.'):
        return get(self._url, path, wd)


def search(url, mask, searchmode='filemask', cs=True):

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

    res = urllib.request.urlopen('{}search?{}'.format(url, data))

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
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

    res = None
    try:
        res = urllib.request.urlopen('{}files?{}'.format(url, data))
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def get(url, path, wd='.', path_is_full=False):

    p = subprocess.Popen(
        ['wget', '--no-check-certificate', '{}download{}'.format(url, path)],
        cwd=wd
        )

    ret = p.wait()

    return ret
