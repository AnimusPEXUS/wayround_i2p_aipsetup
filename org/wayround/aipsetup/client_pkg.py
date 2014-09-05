
import functools
import http.client
import json
import os.path
import subprocess
import tempfile
import urllib.parse
import urllib.request

import org.wayround.aipsetup.package_name_parser
import org.wayround.utils.path


class PackageServerClient:

    def __init__(
        self,
        url, downloads_dir='/tmp/aipsetup_downloads',
        acceptable_extensions_order_list=None
        ):
        self.acceptable_extensions_order_list = \
            acceptable_extensions_order_list
        self.downloads_dir = downloads_dir
        self._url = url
        return

    def walk(self, path):
        return walk(self._url, path)

    def get_recurcive_package_list(self, path):
        return get_recurcive_package_list(self._url, path)

    def list_(self, mask, searchmode='filemask', cs=True):
        return list_(self._url, mask, searchmode, cs)

    def ls(self, path):
        return ls(self._url, path)

    def info(self, pkg_name):
        return info(self._url, pkg_name)

    def asps(self, pkg_name):
        return asps(self._url, pkg_name)

    def asps_latest(self, pkg_name):
        return asps_latest(self._url, pkg_name)

    def get_asp(self, filename, out_dir=None, out_to_temp=False):
        return get_asp(self._url, filename, out_dir, out_to_temp)

    def get_latest_asp(self, pkg_name, out_dir=None, out_to_temp=False):
        return get_latest_asp(self._url, pkg_name, out_dir, out_to_temp)

    def tarballs(self, pkg_name):
        return tarballs(self._url, pkg_name)

    def tarballs_latest(self, pkg_name):
        return tarballs_latest(
            self._url, pkg_name, self.acceptable_extensions_order_list
            )

    def name_by_name(self, tarball):
        return name_by_name(self._url, tarball)

    def bundles(self):
        return bundles(self._url)

    def bundle_get(self, name):
        return bundle_get(self._url, name)


def walk(url, path):

    """
    path must be string not starting and not ending with slash
    """

    res = ls(url, path)

    if res != None:

        cats = res['categories']
        packs = res['packages']

        yield path, cats, packs

        for i in cats:

            sep = ''
            if path != '':
                sep = '/'

            for j in walk(url, '{}{}{}'.format(path, sep, i)):
                yield j

    return


def get_recurcive_package_list(url, path):

    pkgs = []
    for i in walk(url, path):
        pkgs += i[2]

    return list(set(pkgs))


def list_(url, mask, searchmode='filemask', cs=True):

    ret = None

    cst = 'off'
    if cs:
        cst = 'on'

    data = urllib.parse.urlencode(
        {
         'mask': mask,
         'searchmode': searchmode,
         'cs': cst,
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen('{}search?{}'.format(url, data))
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def ls(url, path):

    """
    path must be string not starting and not ending with slash
    """

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}category/{}?{}'.format(url, path, data)
            )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def info(url, pkg_name):

    """
    path must be string not starting and not ending with slash
    """

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}package/{}?{}'.format(url, pkg_name, data)
            )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def asps(url, pkg_name):

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}package/{}/asps?{}'.format(url, pkg_name, data)
        )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def asps_latest(url, pkg_name):

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}package/{}/asps?{}'.format(url, pkg_name, data)
        )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    if ret and len(ret) != 0:
        ret.sort(
            key=functools.cmp_to_key(
                org.wayround.aipsetup.version.package_version_comparator
                ),
            reverse=True
            )
        ret = ret[0]
    else:
        ret = None

    return ret


def get_asp(url, filename, out_dir=None, out_to_temp=False):

    """
    if out_to_temp is True, out_dir is used as a base. Else, if out_dir not
    None, out_dir is used deirectly. if out_dir is None, then out_to_temp
    does not metter and file wil be downloaded to current dir
    """

    ret = None

    parsed = org.wayround.aipsetup.package_name_parser.package_name_parse(
        filename
        )

    basename = os.path.basename(filename)

    sep = ''

    if out_dir == None:

        out_to_temp = False
        out_dir = ''
        sep = ''

    else:
        try:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir, exist_ok=True)
        except:
            pass

        if out_to_temp == True:
            out_dir = tempfile.mkdtemp(
                prefix='{}-tmpdir-'.format(basename),
                dir=out_dir
                )

        if out_dir != '':
            sep = os.path.sep

    try:
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
    except:
        pass

    option_O = '{}{}{}'.format(out_dir, sep, basename)

    pkg_name = parsed['groups']['name']

    p = subprocess.Popen(
        ['wget',
         '--no-check-certificate', '-c', '-O', option_O,
         '{}package/{}/asps/{}'.format(
            url,
            pkg_name,
            basename
            )
         ]
        )

    res = p.wait()

    if res != 0:
        ret = res
    else:
        ret = org.wayround.utils.path.abspath(option_O)

    return ret


def get_latest_asp(url, pkg_name, out_dir=None, out_to_temp=False):

    ret = None

    ltst = asps_latest(url, pkg_name)

    if ltst != None:
        ret = get_asp(url, ltst, out_dir, out_to_temp)

    return ret


def tarballs(url, pkg_name):

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}package/{}/tarballs?{}'.format(url, pkg_name, data)
        )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def tarballs_latest(url, pkg_name, acceptable_extensions_order_list):

    """
    Full url returned
    """

    def source_version_comparator(v1, v2):
        return org.wayround.utils.version.source_version_comparator(
            v1, v2,
            acceptable_extensions_order_list
            )

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}package/{}/tarballs?{}'.format(url, pkg_name, data)
        )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    if ret and len(ret) == 0:
        ret = None

    if isinstance(ret, list):
        m = None
        if len(ret) != 0:
            m = max(
                ret,
                key=functools.cmp_to_key(
                    source_version_comparator
                    )
                )

        # remain only packages with same version, but with different extensions
        for i in ret[:]:
            if (org.wayround.utils.version.source_version_comparator(
                    i, m,
                    acceptable_extensions_order_list
                    )
                != 0):

                ret.remove(i)

    return ret


def get_tarball(
    full_url, out_dir=None, out_to_temp=False,
    mute_downloader=True
    ):

    """
    Download file

    if out_to_temp is True, out_dir is used as a base. Else, if out_dir not
    None, out_dir is used directly. if out_dir is None, then out_to_temp
    does not metter and file will be downloaded to current dir.

    Return: abspath to file on success
    """

    if not isinstance(full_url, str):
        raise TypeError("`full_url' must be str")

    ret = 1

    basename = os.path.basename(full_url)

    sep = ''

    if out_dir == None:

        out_to_temp = False
        out_dir = ''
        sep = ''

    else:
        try:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir, exist_ok=True)
        except:
            pass

        if out_to_temp == True:
            out_dir = tempfile.mkdtemp(
                prefix='{}-tmpdir-'.format(basename),
                dir=out_dir
                )

        if out_dir != '':
            sep = os.path.sep

    try:
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
    except:
        pass

    option_O = '{}{}{}'.format(out_dir, sep, basename)

    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL
    if not mute_downloader:
        stdout = None
        stderr = None

    p = subprocess.Popen(
        ['wget',
         '--no-check-certificate', '-c', '-O', option_O, full_url
         ],
        stdout=stdout,
        stderr=stderr
        )

    res = p.wait()

    if res != 0:
        ret = res
    else:
        ret = org.wayround.utils.path.abspath(option_O)

    return ret


def name_by_name(url, tarball):

    """
    find package name by tarball name
    """

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json',
         'tarball': tarball
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}name_by_name?{}'.format(url, data)
            )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def bundles(url):

    ret = None

    data = urllib.parse.urlencode(
        {
         'resultmode': 'json'
         },
        encoding='utf-8'
        )

    res = None
    try:
        res = urllib.request.urlopen(
            '{}bundles?{}'.format(url, data)
        )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret


def bundle_get(url, name):

    ret = None

    res = None
    try:
        res = urllib.request.urlopen(
            '{}bundles/{}'.format(url, name)
        )
    except:
        pass

    if isinstance(res, http.client.HTTPResponse) and res.status == 200:
        ret = json.loads(str(res.read(), 'utf-8'))

    return ret
