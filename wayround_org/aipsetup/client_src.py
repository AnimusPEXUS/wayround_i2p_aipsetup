
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

    def files(self, name, paths):
        return files(self._url, name, paths)

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


def files(url, name, paths):

    _debug = False

    ret = None

    pre_data = {
        'resultmode': 'json',
        'name': name
        }

    if paths is not None:
        pre_data['paths'] = json.dumps(paths)

    data = urllib.parse.urlencode(
        pre_data,
        encoding='utf-8'
        )

    if _debug:
        print("Data to send:\n{}".format(data))

    res = None
    try:
        res = urllib.request.urlopen('{}files?{}'.format(url, data))
    except:
        logging.exception("Can't get file list from source server")

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
