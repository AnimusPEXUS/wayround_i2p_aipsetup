
"""
Client for searching and getting files on and from aipsetup package server
"""

import urllib.request, urllib.parse
import logging


import org.wayround.aipsetup.config
import org.wayround.aipsetup.version
import org.wayround.aipsetup.name
import org.wayround.aipsetup.pkgindex

def cli_name():
    return 'client'


def exported_commands():
    return {
        }

def commands_order():
    return [
        ]

def client(url):

    t_url = '{proto}://{host}{port}{path}{url}'.format(
        proto=org.wayround.aipsetup.config.config['client_proto'],
        host=org.wayround.aipsetup.config.config['client_host'],
        port=org.wayround.aipsetup.config.config['client_port'],
        path=org.wayround.aipsetup.config.config['client_path'],
        url=url
        )

    u = urllib.request.urlopen(t_url)

    return u

def package_list(category=None):
    u = None
    try :
        u = client('package_list?category={}'.format(urllib.parse.quote(category)))
    except:
        logging.exception("Can't get package list in category {}".format(category))
    else:
        txt = u.read()

    return

def package_info(name):
    return

def package_sources(name):
    return

def package_asps(name):
    return

def category_list(name):
    return

