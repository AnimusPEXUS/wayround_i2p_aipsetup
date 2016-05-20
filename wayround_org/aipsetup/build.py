
"""
Build software before packaging

This module provides functions for building package using building script (see
:mod:`buildscript<wayround_org.aipsetup.buildscript>` module for more info on
building scripts)
"""

import copy
import json
import logging
import os
import pprint
import shutil
import subprocess
import tempfile
import importlib
import types
import collections
import re
import glob

import wayround_org.aipsetup.client_pkg
import wayround_org.aipsetup.controllers
import wayround_org.aipsetup.info
import wayround_org.utils.format.elf
import wayround_org.utils.path
import wayround_org.utils.system_type
import wayround_org.utils.tarball
import wayround_org.utils.terminal
import wayround_org.utils.time


DIR_TARBALL = '00.TARBALL'
"""
Directory for storing tarballs used in package building. contents is packed
into resulting  package as  it is requirements  of most  good licenses
"""

DIR_SOURCE = '01.SOURCE'
"""
Directory for detarred sources, which used for building package. This is not
packed  into final  package,  as we  already  have original  tarballs.
"""

DIR_PATCHES = '02.PATCHES'
"""
Patches stored here. packed.
"""

DIR_BUILDING = '03.BUILDING'
"""
Here package are build. not packed.
"""

DIR_DESTDIR = '04.DESTDIR'
"""
Primary root of files for package. those will be installed into target system.
"""

DIR_BUILD_LOGS = '05.BUILD_LOGS'
"""
Various building logs are stored here. Packed.
"""

DIR_LISTS = '06.LISTS'
"""
Various lists stored here. Packed.
"""

DIR_TEMP = '07.TEMP'
"""
Temporary directory used by aipsetup while building package. Throwed away.
"""


DIR_ALL = [
    DIR_TARBALL,
    DIR_SOURCE,
    DIR_PATCHES,
    DIR_BUILDING,
    DIR_DESTDIR,
    DIR_BUILD_LOGS,
    DIR_LISTS,
    DIR_TEMP
    ]
'All package directories list in proper order'

DIR_LIST = DIR_ALL
':data:`DIR_ALL` copy'


# WARNING: this list is suspiciously similar to what in complete
#          function, but actually they must be separate

PACK_FUNCTIONS_LIST = [
    'destdir_verify_paths_correctness',
    'destdir_set_modes',
    'destdir_checksum',
    'destdir_filelist',
    'destdir_deps_bin',
    'compress_patches_destdir_and_logs',
    'compress_files_in_lists_dir',
    'make_checksums_for_building_site',
    'pack_buildingsite'
    ]
"""
aipsetup CLI related functionality
"""

FUNCTIONS_SET = frozenset(PACK_FUNCTIONS_LIST)
"""
aipsetup CLI related functionality
"""

APPLY_DESCR = """\

    It is typically used in conjunction with functions
    :func:`apply_constitution_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`
    in  this order by function :func:`apply_info`
"""

ROOT_MULTIHOST_DIRNAME = 'multihost'

MULTIHOST_MULTIARCH_DIRNAME = 'multiarch'

MULTIHOST_CROSSBULDERS_DIRNAME = 'crossbuilders'


def _constitution_configurer_sub01(
        value, config, package_info, name,

        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        ):

    if value is None:
        try:
            value = package_info['constitution'][name]
        except:
            try:
                value = config['system_settings'][name]
            except:
                raise Exception(
                    "Can't get `{}' value for package"
                    ", as it is not in package constitution"
                    ", nor in system settings.".format(name)
                    )
                value = None

    else:

        value_l = value.lower()

        if value_l in ['n', 'none', 'no', 'off', '0']:
            value = None

        elif value == 'cfg':
            if config is None:
                raise Exception("system configuration error")
            value = config['system_settings'][name]
        elif value == 'pi':
            if package_info is None:
                raise Exception("package info not configured")
            value = package_info['constitution'][name]

        else:
            re_res = re.match(
                r'^(?P<bhta>(b(uild)?)|(h(ost)?)|(t(arget)?)|(a(rch)?))'
                r'(?P<bhta_o>[ps]?)$',
                value_l
                )
            if re_res is None:
                # raise Exception("invalid parameter value")
                pass

            else:
                bhta = re_res.group('bhta')
                bhta_o = re_res.group('bhta_o')

                if bhta_o == 'p':
                    ss = package_info['constitution']
                elif bhta_o == 's':
                    ss = config['system_settings']
                else:
                    ss = {
                        'host': host_from_param,
                        'build': build_from_param,
                        'target': target_from_param,
                        'arch': arch_from_param
                        }

                if bhta in ['h', 'host']:
                    value = ss['host']

                elif bhta in ['b', 'build']:
                    value = ss['build']

                elif bhta in ['t', 'target']:
                    value = ss['target']

                elif bhta in ['a', 'arch']:
                    value = ss['arch']

    return value


def constitution_configurer(
        config,
        package_info,
        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        ):

    _debug = True

    if _debug:
        logging.info("in host_from_param: {}".format(host_from_param))
        logging.info("in build_from_param: {}".format(build_from_param))
        logging.info("in target_from_param: {}".format(target_from_param))
        logging.info("in arch_from_param: {}".format(arch_from_param))

    host_from_param = _constitution_configurer_sub01(
        host_from_param,
        config,
        package_info,
        'host',
        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        )

    build_from_param = _constitution_configurer_sub01(
        build_from_param,
        config,
        package_info,
        'build',
        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        )

    target_from_param = _constitution_configurer_sub01(
        target_from_param,
        config,
        package_info,
        'target',
        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        )

    arch_from_param = _constitution_configurer_sub01(
        arch_from_param,
        config,
        package_info,
        'arch',
        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        )

    ccp_res = calculate_CC_constitution_parts(
        host_from_param,
        build_from_param,
        target_from_param,
        arch_from_param
        )

    if _debug:
        logging.info("out host_from_param: {}".format(host_from_param))
        logging.info("out build_from_param: {}".format(build_from_param))
        logging.info("out target_from_param: {}".format(target_from_param))
        logging.info("out arch_from_param: {}".format(arch_from_param))
        for i in sorted(list(ccp_res.keys())):
            logging.info("out {}".format(i))

    return (host_from_param, build_from_param, target_from_param,
            arch_from_param, ccp_res)


def calculate_CC_constitution_parts(
        host_str,
        build_str,
        target_str,
        arch_str
        ):

    # this should result in error in Constitution constructor
    ret_multilibs = None
    ret_CC = None
    ret_CXX = None

    if (
        host_str == build_str == target_str
            and (
                (arch_str is not None and arch_str == host_str)
                or
                (arch_str is None)
                )
            and (host_str == 'x86_64-pc-linux-gnu')
            ):
        ret_multilibs = ['m64']
        ret_CC = 'x86_64-pc-linux-gnu-gcc'
        ret_CXX = 'x86_64-pc-linux-gnu-g++'

    elif (
        host_str == build_str == target_str
            and (arch_str is not None and arch_str == 'i686-pc-linux-gnu')
            and (host_str == 'x86_64-pc-linux-gnu')
            ):
        ret_multilibs = ['m32']
        ret_CC = 'x86_64-pc-linux-gnu-gcc'
        ret_CXX = 'x86_64-pc-linux-gnu-g++'

    else:
        logging.warning("""\
Unsupported configuration encountered:
    host:   {}
    build:  {}
    target: {}
    arch:   {}
""".format(
            host_str,
            build_str,
            target_str,
            arch_str
            )
            )

    ret = {
        'multilib_variants': ret_multilibs,
        'CC': ret_CC,
        'CXX': ret_CXX
        }

    return ret


class Constitution:

    def __init__(
            self,
            host_str=None,
            build_str=None,
            target_str=None,
            arch_str=None,
            multilib_variants=None,
            CC=None,
            CXX=None
            ):

        self.host = None
        self.build = None
        self.target = None

        self.arch = None

        if (not isinstance(multilib_variants, list)
                or len(multilib_variants) == 0
            ):
            raise ValueError("`multilib_variant' must be not empty list")

        if not isinstance(arch_str, str):
            raise ValueError("`arch_str' must be str")

        if host_str is not None:
            self.host = wayround_org.utils.system_type.SystemType(host_str)

        if build_str is not None:
            self.build = wayround_org.utils.system_type.SystemType(build_str)

        if target_str is not None:
            self.target = wayround_org.utils.system_type.SystemType(target_str)

        if arch_str is not None:
            self.arch = \
                wayround_org.utils.system_type.SystemType(arch_str)

        self.multilib_variants = sorted(multilib_variants)

        self.CC = CC
        self.CXX = CXX

        return

    def return_aipsetup3_compliant(self):
        ret = collections.OrderedDict(
            [
                ('system_title', 'LAILALO'),
                ('system_version', '4.0'),
                ('host', None),
                ('build', None),
                ('target', None),
                ('arch', None),
                ('multilib_variants', None),
                ('CC', None),
                ('CXX', None),
                ]
            )

        if self.host is not None:
            ret['host'] = str(self.host)
        else:
            ret['host'] = None

        if self.build is not None:
            ret['build'] = str(self.build)
        else:
            ret['build'] = None

        if self.target is not None:
            ret['target'] = str(self.target)
        else:
            ret['target'] = None

        if self.arch is not None:
            ret['arch'] = str(self.arch)
        else:
            ret['arch'] = None

        ret['multilib_variants'] = self.multilib_variants
        ret['CC'] = self.CC
        ret['CXX'] = self.CXX

        return ret


class BuildScriptCtrl:

    def __init__(self):
        return

    def load_buildscript(self, name):
        """
        Loads building script with exec function and returns it's global
        dictionary. ``None`` is returned in case of error.
        """

        ret = None

        if not type(name) == str or not name.isidentifier():
            logging.error(
                "Invalid build module name `{}'".format(name)
                )
            ret = 1

        if not isinstance(ret, int):

            try:
                module = importlib.import_module(
                    'wayround_org.aipsetup.builder_scripts.{}'.format(name)
                    )
            except:
                logging.exception(
                    "Error loading build script `{}'".format(name)
                    )
                ret = 2

            else:

                ret = module

        return ret


class BuildCtl:

    def __init__(
            self,
            buildingsite_ctl
            ):

        if not isinstance(
                buildingsite_ctl,
                BuildingSiteCtl
                ):
            raise TypeError(
                "buildingsite_ctl must be an instance of "
                "wayround_org.aipsetup.build.BuildingSiteCtl"
                )

        self.buildingsite_ctl = buildingsite_ctl
        self.path = wayround_org.utils.path.abspath(buildingsite_ctl.path)
        return

    def complete(self, buildscript_ctl):
        """
        Run all building script commands on selected building site

        See :func:`start_building_script`
        """
        return self.start_building_script(buildscript_ctl, action=None)

    def start_building_script(self, buildscript_ctl, action=None):
        """
        Run selected action on building site using particular building script.

        :param building_site: path to building site directory

        :param action: can be None or concrete name of action in building
            script. if action name ends with + (plus) all remaining actions
            will be also started (if not error will occur)

        :rtype: 0 - if no error occurred
        """

        if not isinstance(buildscript_ctl, BuildScriptCtrl):
            raise ValueError(
                "buildscript_ctl must be of type "
                "wayround_org.aipsetup.build.BuildScriptCtrl"
                )

        building_site = wayround_org.utils.path.abspath(self.path)

        package_info = self.buildingsite_ctl.read_package_info(
            ret_on_error=None
            )

        ret = 0

        if package_info is None:
            logging.error(
                "Error getting information "
                "from building site's(`{}') `package_info.json'".format(
                    building_site
                    )
                )
            ret = 1

        if ret == 0:

            script = buildscript_ctl.load_buildscript(
                package_info['pkg_info']['buildscript']
                )

            if type(script) != types.ModuleType:
                logging.error("Some error while loading builder module")
                ret = 2

        if ret == 0:

            if hasattr(script, 'Builder'):
                try:
                    builder = script.Builder(self.buildingsite_ctl)
                except:
                    logging.exception(
                        "Error initiating builder `{}'".format(
                            script.Builder
                            )
                        )
                    ret = 5

                if ret == 0:

                    if action == 'help':
                        builder.print_help()
                    else:

                        try:
                            actions_container = builder.get_defined_actions()
                        except:
                            logging.exception(
                                "Error getting defined"
                                " actions from `{}'".format(
                                    script
                                    )
                                )
                            ret = 4

                        if ret == 0:

                            try:
                                ret = self.run_builder_action(
                                    self.buildingsite_ctl.getDIR_BUILD_LOGS(),
                                    actions_container,
                                    action=action
                                    )
                            except KeyboardInterrupt:
                                raise
                            except:
                                logging.exception(
                                    "Error running action"
                                    " `{}' in Builder class".format(
                                        action
                                        )
                                    )
                                ret = 3

                        logging.info(
                            "action `{}' ended with code {}".format(
                                action,
                                ret
                                )
                            )

            elif hasattr(script, 'main'):

                try:
                    ret = script.main(building_site, action)
                except KeyboardInterrupt:
                    raise
                except:
                    logging.exception(
                        "Error starting `main' function in `{}'".format(
                            package_info['pkg_info']['buildscript']
                            )
                        )
                    ret = 3

                logging.info(
                    "action `{}' ended with code {}".format(action, ret)
                    )
            else:
                logging.error("Invalid build script structure")
                ret = 4

        return ret

    def run_builder_action(
            self,
            log_output_directory,
            actions_container_object,
            action=None
            ):

        # TODO: add support for list of 2-tuples

        if not isinstance(
                actions_container_object,
                collections.OrderedDict
                ):
            raise TypeError("`actions_container_object' must be OrderedDict")

        ret = 0

        actions = list(actions_container_object.keys())

        if action is not None and isinstance(action, str):
            if action.endswith('+'):
                actions = actions[actions.index(action[:-1]):]
            else:
                actions = [actions[actions.index(action)]]

        for i in actions:

            package_info = self.buildingsite_ctl.read_package_info(
                ret_on_error=None
                )

            log = wayround_org.utils.log.Log(
                log_output_directory,
                '{} {}'.format(
                    package_info['pkg_info']['name'], i
                    )
                )

            log.info(
                "=>------[Starting '{}' action".format(i)
                )
            try:
                ret = actions_container_object[i](i, log)
            except KeyboardInterrupt:
                raise
            except:
                log.exception(
                    "=>------[Exception on '{}' action".format(i)
                    )
                ret = 100
            else:
                log.info(
                    "=>------[Finished '{}' action with code {}".format(
                        i, ret
                        )
                    )

            # NOTE: log closes it self automatically now
            # log.close()

            if ret != 0:
                break

        return ret


def _destdir_filelist(name_to_store_in, destdir, lists_dir):

    ret = 0

    logging.info("Creating file lists")

    destdir = destdir

    lists_dir = lists_dir

    output_file = wayround_org.utils.path.abspath(
        wayround_org.utils.path.join(
            lists_dir,
            name_to_store_in
            )
        )

    os.makedirs(lists_dir, exist_ok=True)

    if not os.path.isdir(destdir):
        logging.error("DESTDIR not found")
        ret = 1

    elif not os.path.isdir(lists_dir):
        logging.error("LIST dir can't be used")
        ret = 2

    else:
        lst = wayround_org.utils.file.files_recurcive_list(destdir)

        lst2 = []
        for i in lst:
            lst2.append('/' + wayround_org.utils.path.relpath(i, destdir))

        lst = lst2

        del lst2

        lst.sort()

        try:
            f = open(output_file, 'w')
        except:
            logging.exception("Can't rewrite file {}".format(output_file))
            ret = 3
        else:

            f.write('\n'.join(lst) + '\n')
            f.close()

    return ret


def _dir_wanisher(
        what_is_being_wanished,
        src_dir,
        dst_dir,
        list_dirs_disasterous_with_pkg_name_exclusion,
        list_package_name_exclusions,
        list_dirs_which_is_disaster,
        list_dirs_which_can_be_safely_moved,
        list_dirs_which_can_be_moved_unless_in_following_list,
        list_packages_which_dirs_not_to_move,
        pkg_name
        ):

    logging.info(
        "{}".format(what_is_being_wanished)
        )

    ret = 0

    if os.path.isdir(src_dir):

        os.makedirs(dst_dir, exist_ok=True)

        if ret == 0:

            for i in list_dirs_disasterous_with_pkg_name_exclusion:

                p1 = wayround_org.utils.path.join(src_dir, i)

                if os.path.islink(p1) or os.path.exists(p1):
                    if not pkg_name in list_package_name_exclusions:
                        logging.error(
                            "Forbidden path: {}".format(
                                wayround_org.utils.path.relpath(p1, src_dir)
                                )
                            )
                        ret = 1
                    else:
                        logging.warning(
                            "Usually forbidden path: {}".format(
                                wayround_org.utils.path.relpath(p1, src_dir)
                                )
                            )
                        logging.warning(
                            "    skipped as packaging for `{}'".format(
                                pkg_name)
                            )

        if ret == 0:
            for i in list_dirs_which_is_disaster:

                p1 = wayround_org.utils.path.join(src_dir, i)

                if os.path.islink(p1) or os.path.exists(p1):
                    logging.error(
                        "Forbidden file or directory: {}".format(
                            wayround_org.utils.path.relpath(p1, src_dir)
                            )
                        )
                    ret = 1

        if ret == 0:
            for i in list_dirs_which_can_be_safely_moved:

                p1 = wayround_org.utils.path.join(src_dir, i)

                if os.path.islink(p1):
                    os.unlink(p1)

                else:
                    if os.path.exists(p1):

                        logging.warning(
                            "    moving: {}".format(
                                os.path.relpath(
                                    p1,
                                    src_dir
                                    )
                                )
                            )

                        wayround_org.utils.file.copytree(
                            p1,
                            wayround_org.utils.path.join(dst_dir, i),
                            dst_must_be_empty=False,
                            verbose=False
                            )
                        # shutil.copytree(p1, destdir + os.path.sep + 'usr')
                        shutil.rmtree(p1)

        if ret == 0:
            for i in list_dirs_which_can_be_moved_unless_in_following_list:

                p1 = wayround_org.utils.path.join(src_dir, i)

                if os.path.islink(p1):
                    os.unlink(p1)

                else:
                    if os.path.exists(p1):

                        if not pkg_name in list_packages_which_dirs_not_to_move:

                            logging.warning(
                                "    moving: {}".format(
                                    os.path.relpath(
                                        p1,
                                        src_dir
                                        )
                                    )
                                )

                            wayround_org.utils.file.copytree(
                                p1,
                                wayround_org.utils.path.join(dst_dir, i),
                                dst_must_be_empty=False,
                                verbose=False
                                )
                            # shutil.copytree(p1, destdir + os.path.sep + 'usr')
                            shutil.rmtree(p1)

                        else:
                            logging.warning(
                                "Usually moved path: {}".format(
                                    wayround_org.utils.path.relpath(
                                        p1,
                                        src_dir)
                                    )
                                )
                            logging.warning(
                                "    skipped as packaging for `{}'".format(
                                    pkg_name
                                    )
                                )
    return ret


class PackCtl:

    def __init__(
            self,
            buildingsite_ctl
            ):

        if not isinstance(
                buildingsite_ctl,
                BuildingSiteCtl
                ):
            raise TypeError(
                "buildingsite_ctl must be an instance of "
                "wayround_org.aipsetup.build.BuildingSiteCtl"
                )

        self.buildingsite_ctl = buildingsite_ctl
        self.path = wayround_org.utils.path.abspath(buildingsite_ctl.path)
        return

    def destdir_chmod(self):
        p = subprocess.Popen(
            ['chmod', '-R', '755', self.path]
            )
        ret = p.wait()
        return ret

    def destdir_filelist(self):
        """
        Create file list for DESTDIR contents
        """

        ret = _destdir_filelist(
            'DESTDIR_orig.lst',
            self.buildingsite_ctl.getDIR_DESTDIR(),
            self.buildingsite_ctl.getDIR_LISTS()
            )

        return ret

    def destdir_verify_paths_correctness(self):

        ret = 0

        logging.info("----------- CHECKS -----------")

        # NOTE: Do not remove '/ -> /usr' and '/usr -> /multihost/xxx'
        #       checks  as many  packages  (including modern  systemd)
        #       still installing files into /  or /usr, but in Lailalo
        #       system it is considered safe  to move those files into
        #       /multihost/xxx

        package_info = self.buildingsite_ctl.read_package_info()
        pkg_name = package_info['pkg_info']['name']

        src_dir = self.buildingsite_ctl.getDIR_DESTDIR()
        dst_dir = wayround_org.utils.path.join(src_dir, 'usr')

        ret = _dir_wanisher(
            '/ -> /usr',
            src_dir,
            dst_dir,
            [],
            [],
            ['mnt', 'multiarch', 'home'],
            ['bin', 'sbin', 'lib', 'lib64'],
            [],
            [],
            pkg_name
            )

        return ret

    def destdir_verify_paths_correctness2(self):

        ret = 0

        package_info = self.buildingsite_ctl.read_package_info()

        pkg_name = package_info['pkg_info']['name']
        host = package_info['constitution']['host']

        src_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'usr'
            )

        dst_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host
            )

        if os.path.exists(src_dir) and os.path.isdir(src_dir):

            lst = os.listdir(src_dir)

            ret = _dir_wanisher(
                '/usr -> /multihost/host',
                src_dir,
                dst_dir,
                [],
                [],
                ['usr', 'multihost'],
                lst,
                [],
                [],
                pkg_name
                )

        wayround_org.utils.file.remove_if_exists(src_dir)

        return ret

    def destdir_verify_paths_correctness3(self):

        ret = 0

        package_info = self.buildingsite_ctl.read_package_info()

        pkg_name = package_info['pkg_info']['name']
        host = package_info['constitution']['host']

        src_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host,
            'usr'
            )

        dst_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host
            )

        if os.path.exists(src_dir) and os.path.isdir(src_dir):
            lst = os.listdir(src_dir)

            ret = _dir_wanisher(
                '/multihost/host/usr -> /multihost/host',
                src_dir,
                dst_dir,
                [],
                [],
                ['usr', 'multihost', 'multiarch', 'local'],
                lst,
                [],
                [],
                pkg_name
                )

        wayround_org.utils.file.remove_if_exists(src_dir)

        return ret

    def destdir_verify_paths_correctness4(self):

        ret = 0

        package_info = self.buildingsite_ctl.read_package_info()

        pkg_name = package_info['pkg_info']['name']

        host = package_info['constitution']['host']
        arch = package_info['constitution']['arch']

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        src_dir = wayround_org.utils.path.join(destdir, 'multihost', host)
        dst_dir = wayround_org.utils.path.join(
            destdir,
            'multihost',
            host,
            'multiarch',
            arch
            )

        ret = _dir_wanisher(
            '/multihost/host -> /multihost/host/multiarch/arch',
            src_dir,
            dst_dir,
            [],
            [],
            ['mnt', 'usr', 'local'],
            #['bin', 'sbin', 'include', 'man', 'info', 'libexec', 'share'],
            [],
            [],
            [],
            pkg_name
            )

        return ret

    def destdir_verify_paths_correctness5(self):

        ret = 0
        return 0
        logging.info("host/share")

        package_info = self.buildingsite_ctl.read_package_info()

        # pkg_name = package_info['pkg_info']['name']

        host = package_info['constitution']['host']
        arch = package_info['constitution']['arch']

        host_share_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host,
            'share',
            )

        tgt_host_share_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host,
            'multiarch',
            arch,
            'share'
            )

        if os.path.isdir(host_share_dir):
            lst = os.listdir(host_share_dir)

            for i in lst:

                if i in ['man', 'doc', 'docs']:

                    jo = wayround_org.utils.path.join(
                        host_share_dir,
                        i
                        )

                    if os.path.isdir(jo):

                        logging.info("    {}".format(i))

                        jo2 = wayround_org.utils.path.join(
                            tgt_host_share_dir,
                            i
                            )

                        os.makedirs(
                            jo2,
                            exist_ok=True
                            )

                        if wayround_org.utils.file.copytree(
                                jo,
                                jo2,
                                overwrite_files=True,
                                clear_before_copy=False,
                                dst_must_be_empty=False,
                                verbose=False
                                ) != 0:
                            ret += 1

                        else:

                            shutil.rmtree(jo)

        if os.path.isdir(host_share_dir):
            if len(os.listdir(host_share_dir)) == 0:
                shutil.rmtree(host_share_dir)
                ret = 0
            else:
                logging.error("host/share dir is not empty")
                ret = 1

        return ret

    def destdir_verify_paths_correctness6(self):

        ret = 0

        package_info = self.buildingsite_ctl.read_package_info()

        pkg_name = package_info['pkg_info']['name']
        host = package_info['constitution']['host']
        arch = package_info['constitution']['arch']

        src_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host,
            'multiarch',
            arch,
            'usr'
            )

        dst_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multihost',
            host,
            'multiarch',
            arch
            )

        if os.path.exists(src_dir) and os.path.isdir(src_dir):
            lst = os.listdir(src_dir)

            ret = _dir_wanisher(
                '/multihost/host/multiarch/arch/usr -> '
                '/multihost/host/multiarch/arch',
                src_dir,
                dst_dir,
                [],
                [],
                ['usr', 'multihost', 'multiarch', 'local'],
                lst,
                [],
                [],
                pkg_name
                )

        wayround_org.utils.file.remove_if_exists(src_dir)

        return ret

    def destdir_verify_paths_correctness7(self):

        ret = 0

        package_info = self.buildingsite_ctl.read_package_info()

        # pkg_name = package_info['pkg_info']['name']

        host = package_info['constitution']['host']
        arch = package_info['constitution']['arch']

        for i in [
                wayround_org.utils.path.join(
                    self.buildingsite_ctl.getDIR_DESTDIR(),
                    'multihost',
                    host,
                    'multiarch',
                    arch
                    ),
                wayround_org.utils.path.join(
                    self.buildingsite_ctl.getDIR_DESTDIR(),
                    'multihost',
                    host,
                    'multiarch'
                    ),
                ]:

            if len(os.listdir(i)) == 0:
                os.rmdir(i)

        logging.info("----------- CHECKS -----------")

        return 0

        package_info = self.buildingsite_ctl.read_package_info()

        pkg_name = package_info['pkg_info']['name']

        host = package_info['constitution']['host']
        arch = package_info['constitution']['arch']

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        src_dir = wayround_org.utils.path.join(
            destdir,
            'multihost',
            host,
            'multiarch',
            arch
            )
        dst_dir = wayround_org.utils.path.join(
            destdir,
            'multihost',
            host
            )

        ret = _dir_wanisher(
            '/multihost/host/multiarch/arch -> /multihost/host',
            src_dir,
            dst_dir,
            [],
            [],  # ['Python2', 'Python3'],
            #['lib64', 'libx32', 'lib32', 'lib'],
            [],
            [],
            [],
            [],
            pkg_name
            )

        logging.info("----------- CHECKS -----------")

        return ret

    def rename_configuration_dirs(self):
        ret = 0

        logging.info("Renaming configuration directories")

        package_info = self.buildingsite_ctl.read_package_info()

        dst_dir = self.buildingsite_ctl.getDIR_DESTDIR()

        host = package_info['constitution']['host']
        arch = package_info['constitution']['arch']

        files = sorted(os.listdir(dst_dir))

        errors = 0

        for i in ['etc', 'var']:

            i_new_name = '{}.distr.{}.{}'.format(i, host, arch)
            src_dir_name = wayround_org.utils.path.join(dst_dir, i)
            target_dir_name = wayround_org.utils.path.join(dst_dir, i_new_name)

            if i in files:

                if os.path.isdir(src_dir_name):
                    if not os.path.exists(target_dir_name):

                        logging.info(
                            "    renaming `{}' to `{}'".format(i, i_new_name)
                            )

                        os.rename(src_dir_name, target_dir_name)

                    else:
                        logging.error(
                            "    `{}' already exists".format(i_new_name)
                            )
                        errors += 1

        del(files)

        # TODO: do I really need this rest of this method?
        # ANSWER: YES

        etc_new_name = '{}.distr.{}.{}'.format('etc', host, arch)

        src_set_dir = wayround_org.utils.path.join(
            dst_dir,
            etc_new_name,
            'profile.d',
            'SET')
        dst_set_dir = wayround_org.utils.path.join(
            dst_dir,
            'etc',
            'profile.d',
            'SET')

        if os.path.isdir(src_set_dir):
            logging.info("Copying profile.d/SET files")
            if wayround_org.utils.file.copy_file_or_directory(
                    src_set_dir,
                    dst_set_dir,
                    overwrite_files=True,
                    clear_before_copy=False,
                    dst_must_be_empty=False,
                    verbose=True
                    ) != 0:
                errors += 1

        return int(errors != 0)

    def relocate_libx_dir_files_into_lib_dir(self):

        raise Exception("We should avoid using this practice")

        ret = 0

        package_info = self.buildingsite_ctl.read_package_info()

        host = package_info['constitution']['host']

        arch_dir = wayround_org.utils.path.join(
            self.buildingsite_ctl.getDIR_DESTDIR(),
            'multiarch',
            host
            )

        lib_dir = wayround_org.utils.path.join(arch_dir, 'lib')

        os.makedirs(lib_dir, exist_ok=True)

        all_files = os.listdir(arch_dir)

        libx_dirs = []

        for i in all_files:
            if i in ['lib64', 'lib32', 'libx32']:
                logging.info("{} contents selected for moving".format(i))
                libx_dirs.append(
                    wayround_org.utils.path.join(
                        arch_dir,
                        i
                        )
                    )

        copy_errors = 0
        for j in libx_dirs:

            j_files = os.listdir(j)

            for i in j_files:
                if wayround_org.utils.file.copy_file_or_directory(
                        wayround_org.utils.path.join(j, i),
                        wayround_org.utils.path.join(lib_dir, i),
                        overwrite_files=False,
                        clear_before_copy=False,
                        dst_must_be_empty=True,
                        verbose=True
                        ) != 0:
                    copy_errors += 1

        if copy_errors != 0:
            logging.error("Some copying error")
            ret = 2

        if ret == 0:
            for i in libx_dirs:
                shutil.rmtree(i)

        return ret

    def destdir_filelist2(self):
        """
        Create file list for DESTDIR contents
        """

        ret = _destdir_filelist(
            'DESTDIR.lst',
            self.buildingsite_ctl.getDIR_DESTDIR(),
            self.buildingsite_ctl.getDIR_LISTS()
            )

        return ret

    def destdir_set_modes(self):
        """
        Ensure all files (and dirs) in DESTDIR have ``0o755`` mode.

        If You interested in defferent modes for files after package
        installation, read about post_install.py (script, which need to be
        placed in package and will be executed after package installation)

        .. TODO: link to info about post_install.py
        """

        logging.info("Resetting files and dirs modes")

        # NOTE: dirs and files all must have 0700 modes!
        #       do not remove execution bit from files!

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        ret = 0

        try:
            for dirpath, dirnames, filenames in os.walk(destdir):
                filenames.sort()
                dirnames.sort()
                dirpath = wayround_org.utils.path.abspath(dirpath)

                for i in dirnames:
                    f = wayround_org.utils.path.join(dirpath, i)
                    if not os.path.islink(f):
                        os.chmod(f, mode=0o755)

                for i in filenames:
                    f = wayround_org.utils.path.join(dirpath, i)
                    if not os.path.islink(f):
                        os.chmod(f, mode=0o755)

        except:
            logging.exception("Modes change exception")
            ret = 1

        return ret

    def destdir_edit_executable_elfs(self):

        # NOTE: this editing need maybe to be done because of nature of
        #       /multiarch dir. In future, Lailalo need to avoid existing of
        #       standard /usr, /bin, /sbin, /lib, /lib64 etc dirs and
        #       as much as possible move everythin under /multiarch
        #       dirs

        raise Exception(
            "Don't do this any more."
            " Better - create symlinks to needed ld-linux files."
            )

        ret = 0

        logging.info(
            "Patching executable ELFs' linker path"
            )

        package_info = self.buildingsite_ctl.read_package_info()

        host = package_info['constitution']['host']

        if not host in [
                'i686-pc-linux-gnu',
                'x86_64-pc-linux-gnu'
                ]:
            raise Exception("Trying to package for unsupported host")

        skip_patch = False

        if package_info['pkg_info']['name'] in [
                'linux',
                #'binutils',
                'glibc',
                #'gcc'
                ] and (
                    package_info['constitution']['build'] !=
                    package_info['constitution']['host']
                    ):
            skip_patch = True

            logging.warning(
                "Skipping pathelf'ing this package, as "
                "possible crossbuild of `{}'".format(
                    package_info['pkg_info']['name']
                    )
                )
            ret = 0

        if not skip_patch:

            dl32 = wayround_org.aipsetup.build.find_dl(
                wayround_org.utils.path.join(
                    '/',
                    'multiarch',
                    'i686-pc-linux-gnu'
                    )
                )

            dl64 = wayround_org.aipsetup.build.find_dl(
                wayround_org.utils.path.join(
                    '/',
                    'multiarch',
                    'x86_64-pc-linux-gnu'
                    )
                )

            logging.info(
                "New values to apply:\n"
                "        for EM_386   : {}\n"
                "        for EM_X86_64: {}"
                "".format(
                    dl32,
                    dl64
                    )
                )

            if dl32 is None or dl64 is None:
                logging.warning(
                    "If would find executable ELF for which have no proper"
                    " linker - error"
                    )

            destdir = self.buildingsite_ctl.getDIR_DESTDIR()

            lists_dir = self.buildingsite_ctl.getDIR_LISTS()

            lists_file = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    lists_dir,
                    'DESTDIR.lst'
                    )
                )

            try:
                f = open(lists_file, 'r')
            except:
                logging.exception("Can't open file list")
            else:
                try:
                    file_list_txt = f.read()
                    file_list = file_list_txt.splitlines()
                    del(file_list_txt)

                    exec_elfs_list = []
                    elfs = 0
                    n_elfs = 0
                    file_list_i = 0
                    file_list_l = len(file_list)
                    for i in file_list:
                        filename = wayround_org.utils.path.abspath(
                            wayround_org.utils.path.join(destdir, i)
                            )

                        if (os.path.isfile(filename)
                                and os.path.exists(filename)):

                            try:
                                elf = wayround_org.utils.format.elf.ELF(
                                    filename)
                            except:
                                logging.exception(
                                    "Error parsing file: `{}'".format(filename)
                                    )
                                n_elfs += 1
                            else:

                                if elf.is_elf:

                                    elfs += 1

                                    if (elf.elf_type_name == 'ET_EXEC'
                                            and elf.dynamic_section is not None):

                                        exec_elfs_list.append(filename)

                                else:
                                    n_elfs += 1
                        else:
                            n_elfs += 1

                        file_list_i += 1

                        wayround_org.utils.terminal.progress_write(
                            "    ({perc:.2f}%) ELFs: {elfs}; non-ELFs: {n_elfs}".
                            format_map(
                                {
                                    'perc':
                                    (100 /
                                     (float(file_list_l) / file_list_i)),
                                        'elfs': elfs,
                                        'n_elfs': n_elfs
                                    }
                                )
                            )

                    wayround_org.utils.terminal.progress_write_finish()

                    logging.info(
                        "    found executable elfs: {}".format(
                            len(exec_elfs_list)
                            )
                        )

                    logging.info(
                        "    going to \"patchelf\" found files"
                        )

                    for i in exec_elfs_list:
                        elf = wayround_org.utils.format.elf.ELF(i)
                        logging.info(
                            "        patching: ({:10}) {}".format(
                                elf.elf_machine_name,
                                os.path.relpath(
                                    i,
                                    destdir
                                    )
                                )
                            )

                        dl_to_use = None
                        if elf.elf_machine_name == 'EM_386':
                            dl_to_use = dl32
                        elif elf.elf_machine_name == 'EM_X86_64':
                            dl_to_use = dl64
                        else:
                            raise Exception("DNA error")

                        if dl_to_use is None:
                            raise Exception("No appropriate linker found")

                        p = subprocess.Popen(
                            ['patchelf', '--set-interpreter', dl_to_use, i]
                            )
                        if p.wait() != 0:
                            logging.error(
                                "Couldn't change interpreter for: {}".format(
                                    i)
                                )
                            ret = 5
                            break

                finally:
                    f.close()
        return ret

    def destdir_checksum(self):
        """
        Create checksums for DESTDIR contents
        """

        ret = 0

        logging.info("Creating checksums")

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

        output_file = wayround_org.utils.path.abspath(
            wayround_org.utils.path.join(
                lists_dir,
                'DESTDIR.sha512'
                )
            )

        try:
            os.makedirs(lists_dir)
        except:
            pass

        if not os.path.isdir(destdir):
            logging.error("DESTDIR not found")
            ret = 1
        elif not os.path.isdir(lists_dir):
            logging.error("LIST dir can't be used")
            ret = 2
        else:
            ret = wayround_org.utils.checksum.make_dir_checksums(
                destdir,
                output_file,
                destdir
                )

        return ret

    def destdir_deps_bin(self):
        """
        Create dependency tree listing for ELFs in DESTDIR
        """

        ret = 0

        logging.info("Generating C deps lists")

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

        lists_file = wayround_org.utils.path.abspath(
            wayround_org.utils.path.join(
                lists_dir,
                'DESTDIR.lst'
                )
            )

        deps_file = wayround_org.utils.path.abspath(
            wayround_org.utils.path.join(
                lists_dir,
                'DESTDIR.dep_c'
                )
            )

        try:
            f = open(lists_file, 'r')
        except:
            logging.exception("Can't open file list")
        else:
            try:
                file_list_txt = f.read()
                file_list = file_list_txt.splitlines()
                del(file_list_txt)

                deps = {}
                elfs = 0
                n_elfs = 0
                file_list_i = 0
                file_list_l = len(file_list)
                for i in file_list:
                    filename = wayround_org.utils.path.abspath(
                        wayround_org.utils.path.join(destdir, i)
                        )

                    if os.path.isfile(filename) and os.path.exists(filename):

                        try:
                            elf = wayround_org.utils.format.elf.ELF(filename)
                        except:
                            logging.exception(
                                "Error parsing file: `{}'".format(filename)
                                )
                            n_elfs += 1
                        else:

                            dep = elf.needed_libs_list

                            if isinstance(dep, list):
                                elfs += 1
                                deps[i] = dep
                            else:
                                n_elfs += 1
                    else:
                        n_elfs += 1

                    file_list_i += 1

                    wayround_org.utils.terminal.progress_write(
                        "    ({perc:.2f}%) ELFs: {elfs}; non-ELFs: {n_elfs}".
                        format_map(
                            {
                                'perc':
                                (100 /
                                 (float(file_list_l) / file_list_i)),
                                    'elfs': elfs,
                                    'n_elfs': n_elfs
                                }
                            )
                        )

                wayround_org.utils.terminal.progress_write_finish()

                logging.info("ELFs: {elfs}; non-ELFs: {n_elfs}".format_map({
                    'elfs': elfs,
                    'n_elfs': n_elfs
                    }))

                try:
                    f2 = open(deps_file, 'w')
                except:
                    logging.exception("Can't create file of dependencies list")
                    raise
                else:
                    try:
                        f2.write(pprint.pformat(deps))
                    finally:
                        f2.close()

            finally:
                f.close()

        return ret

    def compress_patches_destdir_and_logs(self):

        ret = 0

        logging.info(
            "Compressing {}, {} and {}".format(
                DIR_PATCHES,
                DIR_DESTDIR,
                DIR_BUILD_LOGS
                )
            )

        for i in [
                DIR_PATCHES,
                DIR_DESTDIR,
                DIR_BUILD_LOGS
                ]:
            dirname = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    self.path,
                    i
                    )
                )
            filename = "{}.tar.xz".format(dirname)

            if not os.path.isdir(dirname):
                logging.warning("Dir not exists: {}".format(dirname))
                ret = 1
                break
            else:
                size = wayround_org.utils.file.get_file_size(dirname)
                logging.info(
                    "Compressing {} (size: {} B ~= {:4.2f} MiB)".format(
                        i,
                        size,
                        float(size) / 1024 / 1024
                        )
                    )

                wayround_org.utils.archive.archive_tar_canonical(
                    dirname,
                    filename,
                    'xz',
                    verbose_tar=False,
                    verbose_compressor=True,
                    additional_tar_options=['--sort=name']
                    )

        return ret

    def compress_files_in_lists_dir(self):

        ret = 0

        logging.info("Compressing files in lists dir")

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

        for i in ['DESTDIR_orig.lst', 'DESTDIR.lst', 'DESTDIR.sha512',
                  'DESTDIR.dep_c']:

            infile = wayround_org.utils.path.join(lists_dir, i)
            outfile = infile + '.xz'

            if wayround_org.utils.exec.process_file(
                    'xz',
                    infile,
                    outfile,
                    stderr=None,
                    options=['-9', '-v', '-M', (200 * 1024 ** 2)]
                    ) != 0:
                logging.error("Error compressing files in lists dir")
                ret = 1
                break

        return ret

    def make_checksums_for_building_site(self):

        ret = 0

        logging.info("Making checksums for buildingsite files")

        buildingsite = wayround_org.utils.path.abspath(self.path)

        package_checksums = wayround_org.utils.path.join(
            buildingsite,
            'package.sha512'
            )

        list_to_checksum = self.get_list_of_items_to_pack()

        if package_checksums in list_to_checksum:
            list_to_checksum.remove(package_checksums)

        for i in list_to_checksum:
            if os.path.islink(i) or not os.path.isfile(i):
                logging.error(
                    "Not exists or not a normal file: {}".format(
                        wayround_org.utils.path.relpath(i, buildingsite)
                        )
                    )
                ret = 10

        if ret == 0:

            check_summs = wayround_org.utils.checksum.checksums_by_list(
                list_to_checksum, method='sha512'
                )

            check_summs2 = {}
            paths = list(check_summs.keys())

            for i in paths:
                check_summs2[
                    '/' + wayround_org.utils.path.relpath(i, buildingsite)
                    ] = check_summs[i]

            check_summs = check_summs2

            del check_summs2

            f = open(package_checksums, 'w')
            f.write(
                wayround_org.utils.checksum.render_checksum_dict_to_txt(
                    check_summs,
                    sort=True
                    )
                )
            f.close()

        return ret

    def pack_buildingsite(self):
        """
        Create new package from building site and place it under ../pack
        deirectory
        """

        ret = 0

        buildingsite = wayround_org.utils.path.abspath(self.path)

        logging.info("Creating package")

        package_info = self.buildingsite_ctl.read_package_info(
            ret_on_error=None
            )

        if package_info is None:
            logging.error("error getting information about package")
            ret = 1
        else:

            pack_dir = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    buildingsite,
                    '..',
                    'pack'
                    )
                )

            pack_file_name = wayround_org.utils.path.join(
                pack_dir,
                "({pkgname})-({version})-({status})-"
                "({timestamp})-({hostinfo})-({arch}).asp".format_map(
                    {
                        'pkgname': package_info['pkg_info']['name'],
                        'version':
                            package_info['pkg_nameinfo']['groups']['version'],
                        'status':
                            package_info['pkg_nameinfo']['groups']['status'],
                        'timestamp':
                            wayround_org.utils.time.currenttime_stamp(),
                        'hostinfo': package_info['constitution']['host'],
                        'arch': package_info['constitution']['arch']
                        }
                    )
                )

            logging.info("Package will be saved as: {}".format(pack_file_name))

            if not os.path.isdir(pack_dir):
                os.makedirs(pack_dir)

            list_to_tar = self.get_list_of_items_to_pack()

            list_to_tar2 = []

            for i in list_to_tar:
                list_to_tar2.append(
                    './' + wayround_org.utils.path.relpath(i, buildingsite)
                    )

            list_to_tar = list_to_tar2

            del list_to_tar2

            list_to_tar.sort()

            try:
                ret = subprocess.Popen(
                    ['tar', '-vcf', pack_file_name] + list_to_tar,
                    cwd=buildingsite
                    ).wait()
            except:
                logging.exception("Error tarring package")
                ret = 30
            else:
                logging.info("ASP package creation complete")
                ret = 0

        return ret

    def complete(self):
        """
        Do all specter of pack operations on building site
        """
        logging.info("Packaging: {}".format(self.path))

        ret = 0

        for i in [
                self.destdir_chmod,
                self.destdir_filelist,
                self.destdir_verify_paths_correctness,
                self.destdir_verify_paths_correctness2,
                self.destdir_verify_paths_correctness3,
                self.destdir_verify_paths_correctness4,
                self.destdir_verify_paths_correctness5,
                self.destdir_verify_paths_correctness6,
                self.destdir_verify_paths_correctness7,
                self.rename_configuration_dirs,
                # self.relocate_libx_dir_files_into_lib_dir,
                self.destdir_filelist2,
                self.destdir_set_modes,
                # self.destdir_edit_executable_elfs,
                self.destdir_checksum,
                self.destdir_deps_bin,
                self.compress_patches_destdir_and_logs,
                self.compress_files_in_lists_dir,
                self.make_checksums_for_building_site,
                self.pack_buildingsite
                ]:

            try:
                i_res = i()
            except:
                logging.exception("Error")
                ret = 2

            if ret == 0:
                if i_res != 0:
                    ret = 1

            if ret != 0:
                logging.error("Error on {}".format(i))
                break

        return ret

    def get_list_of_items_to_pack(self):

        building_site = wayround_org.utils.path.abspath(self.path)

        ret = []

        ret.append(
            wayround_org.utils.path.join(
                building_site,
                DIR_DESTDIR + '.tar.xz'
                )
            )

        ret.append(
            wayround_org.utils.path.join(
                building_site,
                DIR_PATCHES + '.tar.xz'
                )
            )

        ret.append(
            wayround_org.utils.path.join(
                building_site,
                DIR_BUILD_LOGS + '.tar.xz'
                )
            )

        ret.append(
            wayround_org.utils.path.join(
                building_site,
                'package_info.json'
                )
            )

        ret.append(
            wayround_org.utils.path.join(
                building_site,
                'package.sha512'
                )
            )

        post_install_script = wayround_org.utils.path.join(
            building_site, 'post_install.py'
            )

        if os.path.isfile(post_install_script):
            ret.append(post_install_script)

        tarballs = os.listdir(
            self.buildingsite_ctl.getDIR_TARBALL()
            )

        for i in tarballs:
            ret.append(
                wayround_org.utils.path.join(
                    building_site,
                    DIR_TARBALL, i
                    )
                )

        lists = os.listdir(
            self.buildingsite_ctl.getDIR_LISTS()
            )

        for i in lists:
            if i.endswith('.xz'):
                ret.append(
                    wayround_org.utils.path.join(
                        building_site,
                        DIR_LISTS, i
                        )
                    )

        return ret


def read_package_info(path, ret_on_error=None):
    bs = BuildingSiteCtl(path)
    return bs.read_package_info(ret_on_error)


class BuildingSiteCtl:

    def __init__(self, path):
        self.path = wayround_org.utils.path.abspath(path)
        return

    def getDIR_TARBALL(self):
        return getDIR_TARBALL(self.path)

    def getDIR_SOURCE(self):
        return getDIR_SOURCE(self.path)

    def getDIR_PATCHES(self):
        return getDIR_PATCHES(self.path)

    def getDIR_BUILDING(self):
        return getDIR_BUILDING(self.path)

    def getDIR_DESTDIR(self):
        return getDIR_DESTDIR(self.path)

    def getDIR_BUILD_LOGS(self):
        return getDIR_BUILD_LOGS(self.path)

    def getDIR_LISTS(self):
        return getDIR_LISTS(self.path)

    def getDIR_TEMP(self):
        return getDIR_TEMP(self.path)

    def isWdDirRestricted(self):
        return isWdDirRestricted(self.path)

    def is_building_site(self):
        return os.path.isfile(
            wayround_org.utils.path.join(self.path, 'package_info.json'))

    def init(self, files=None):
        """
        Initiates building site path for farther package build.

        Files in named directory are not deleted if it is already exists.

        :rtype: returns 0 if no errors
        """

        ret = 0

        path = wayround_org.utils.path.abspath(self.path)

        logging.info("Initiating building site `{}'".format(path))

        logging.info("Checking dir name safety")

        if self.isWdDirRestricted():
            logging.error(
                "`{}' is restricted working dir -- won't init".format(path)
                )
            ret = -1

        # if exists and not derictory - not continue
        if ret == 0:

            if ((os.path.exists(path))
                    and not os.path.isdir(path)):
                logging.error(
                    "File already exists and it is not a building site"
                    )
                ret = -2

        if ret == 0:

            if not os.path.exists(path):
                logging.info("Building site not exists - creating")
                os.mkdir(path)

            logging.info("Creating required subdirs")
            for i in DIR_ALL:
                a = wayround_org.utils.path.abspath(
                    wayround_org.utils.path.join(
                        path,
                        i))

                if not os.path.exists(a):
                    resh = 'creating'
                elif not os.path.isdir(a):
                    resh = 'not a dir!'
                elif os.path.islink(a):
                    resh = 'is a link!'
                else:
                    resh = 'exists'

                print("       {dirname} - {resh}".format_map({
                    'dirname': i,
                    'resh': resh
                    })
                    )

                if os.path.exists(a):
                    pass
                else:
                    os.makedirs(a)

        if ret == 0:
            logging.info("Init complete")

            if isinstance(files, list):

                if len(files) > 0:
                    t_dir = self.getDIR_TARBALL()

                    for i in files:
                        logging.info("Copying file {}".format(i))
                        shutil.copy2(i, t_dir)

        else:
            logging.error("Init error")

        return ret

    def read_package_info(self, ret_on_error=None):
        """
        Reads package info applied to building site

        :rtype: ``ret_on_error`` parameter contents on error (``None`` by
            default)
        """

        path = wayround_org.utils.path.abspath(self.path)

        logging.debug(
            "Trying to read package info in building site `{}'".format(path)
            )

        ret = ret_on_error

        pi_filename = wayround_org.utils.path.join(path, 'package_info.json')

        if not os.path.isfile(pi_filename):
            logging.error("`{}' not found".format(pi_filename))
            ret = ret_on_error
        else:
            txt = ''
            f = None
            try:
                f = open(pi_filename, 'r')
            except:
                logging.exception("Can't open `{}'".format(pi_filename))
                ret = ret_on_error
            else:
                txt = f.read()
                f.close()
                try:
                    ret = json.loads(txt)
                except:
                    logging.exception("Error in `{}'".format(pi_filename))
                    ret = ret_on_error
        return ret

    def write_package_info(self, info):
        """
        Writes given info to given building site

        Raises exceptions in case of errors
        """

        path = wayround_org.utils.path.abspath(self.path)

        ret = 0

        package_information_filename = wayround_org.utils.path.join(
            path,
            'package_info.json')

        f = None

        try:
            f = open(package_information_filename, 'w')
        except:
            raise Exception(
                "Can't open `{}' for writing".format(
                    package_information_filename
                    )
                )
        else:
            try:
                txt = ''
                try:
                    txt = json.dumps(
                        info,
                        allow_nan=False,
                        indent=2,
                        sort_keys=True
                        )
                except:
                    logging.exception("Can't parse package_info.json text")
                    ret = 1
                else:
                    f.write(txt)

            finally:
                f.close()

        return ret

    def set_pkg_main_tarball(self, filename):
        """
        Set main package tarball in case there are many of them.
        """

        base = os.path.basename(filename)

        package_info = self.read_package_info({})

        parse_result = wayround_org.utils.tarball.parse_tarball_name(base)

        if not isinstance(parse_result, dict):
            logging.error("Can't correctly parse file name")
            package_info['pkg_nameinfo'] = {}
            ret = 1
        else:
            package_info['pkg_nameinfo'] = parse_result
            ret = 0

        self.write_package_info(package_info)

        return ret

    def get_pkg_main_tarball(self):
        """
        Get main package tarball in case there are many of them.
        """

        r = self.read_package_info({})

        try:
            ret = r['pkg_nameinfo']['name']
        except:
            ret = ''

        return ret

    def apply_pkg_nameinfo_on_buildingsite(self, filename):
        """
        Applies package name parsing result on building site package info
        """

        ret = 0

        if filename is None:
            logging.info(
                "You didn't supplyed tarball name, so trying to find out.."
                )
            nameinfo_name = self.get_pkg_main_tarball()

            if nameinfo_name != '':
                filename = nameinfo_name
            else:
                logging.info(
                    "package_info.json has no main tarball name,"
                    " so looking in 00.TARBALLS dir"
                    )

                tar_dir = self.getDIR_TARBALL()

                tar_files = os.listdir(tar_dir)

                if len(tar_files) != 1:

                    logging.error(
                        "Can't decide which tarball to use. "
                        "File in 00.TARBALLS is not single"
                        )
                    ret = 1

                else:
                    filename = tar_files[0]

        if ret == 0:
            logging.info("main tarball is recognized as: {}".format(filename))
            ret = self.set_pkg_main_tarball(filename)

        return ret

    apply_pkg_nameinfo_on_buildingsite.__doc__ += APPLY_DESCR

    def apply_constitution_on_buildingsite(self, const):
        """
        Applies constitution on building site package info
        """

        if not isinstance(const, Constitution):
            raise ValueError(
                "const must be of type "
                "wayround_org.aipsetup.build.Constitution"
                )

        ret = 0

        package_info = self.read_package_info(ret_on_error={})

        const = const.return_aipsetup3_compliant()

        if const is None:
            ret = 1

        else:
            package_info['constitution'] = const
            self.write_package_info(package_info)

        return ret

    apply_constitution_on_buildingsite.__doc__ += APPLY_DESCR

    def apply_pkg_info_on_buildingsite(self, pkg_client, package_name=None):
        """
        Applies package information on building site package info

        if package_name is None and can't be taken from package_info.json
        file - it will be asked from info server to parse
        tarball name and determine package info name. If returned not one -
        this is error.
        """

        ret = 0

        if not isinstance(
                pkg_client,
                wayround_org.aipsetup.client_pkg.PackageServerClient
                ):
            raise TypeError(
                "pkg_client must be of type "
                "wayround_org.aipsetup.client_pkg.PackageServerClient"
                )

        package_info = self.read_package_info(ret_on_error={})

        if package_name is None:
            try:
                package_name = package_info['pkg_info']['name']
            except:
                logging.exception(
                    "Can't get package_info['pkg_info']['name']. "
                    "Asking server.."
                    )
                package_name = None

        if package_name is None:

            ret = 6

            try:
                isinstance(package_info['pkg_nameinfo']['name'], str)
            except:
                logging.exception(
                    "package_info['pkg_nameinfo']['name'] undetermined"
                    )
                package_info['pkg_info'] = {}
                ret = 1

            else:

                logging.info(
                    "Getting info from index DB for: {}".format(
                        package_info['pkg_nameinfo']['name']
                        )
                    )

                n_b_n = pkg_client.name_by_name(
                    package_info['pkg_nameinfo']['name']
                    )

                if len(n_b_n) != 1:
                    logging.error(
                        "Can't select between package names:\n    {}".format(
                            n_b_n
                            )
                        )
                    ret = 5

                else:

                    package_name = n_b_n[0]
                    logging.info(
                        "Package name determined by server: {}".format(
                            package_name
                            )
                        )
                    ret = 0

            if ret == 0:

                logging.info(
                    "Getting full package info for name: {}".format(
                        package_name
                        )
                    )
                info = pkg_client.info(package_name)

                if not isinstance(info, dict):
                    logging.error("Can't read info from DB")
                    package_info['pkg_info'] = {}
                    ret = 4

                else:

                    package_info['pkg_info'] = info
                    self.write_package_info(package_info)

                    ret = 0

        return ret

    apply_pkg_info_on_buildingsite.__doc__ += APPLY_DESCR

    def _apply_info_common01(self, pkg_client, const):

        if not isinstance(const, Constitution):
            raise ValueError(
                "const must be of type "
                "wayround_org.aipsetup.build.Constitution"
                )

        if not isinstance(
                pkg_client,
                wayround_org.aipsetup.client_pkg.PackageServerClient
                ):
            raise TypeError(
                "pkg_client must be of type "
                "wayround_org.aipsetup.client_pkg.PackageServerClient"
                )

        return

    def apply_info(self, pkg_client, const, src_file_name=None):
        """
        Apply package information to building site
        """

        self._apply_info_common01(pkg_client, const)

        path = wayround_org.utils.path.abspath(self.path)

        ret = 0

        tar_dir = self.getDIR_TARBALL()

        if self.get_pkg_main_tarball() == '':
            if not isinstance(src_file_name, str):
                tar_files = os.listdir(tar_dir)

                if len(tar_files) != 1:
                    logging.error("Can't decide which tarball to use")
                    ret = 15
                else:
                    src_file_name = tar_files[0]
                    self.set_pkg_main_tarball(src_file_name)

        if ret == 0:

            if self.read_package_info(None) is None:
                logging.info(
                    "Applying new package info to dir `{}'".format(
                        wayround_org.utils.path.abspath(
                            path
                            )
                        )
                    )

                self.write_package_info({})

            if self.apply_pkg_nameinfo_on_buildingsite(src_file_name) != 0:
                ret = 1

            if ret == 0:
                if self.apply_constitution_on_buildingsite(const) != 0:
                    ret = 2

            if ret == 0:
                if self.apply_pkg_info_on_buildingsite(pkg_client) != 0:
                    ret = 3

            else:
                # no error
                pass

        return ret

    def apply_info_by_name(self, pkg_client, const, package_name):
        """
        Apply package information to building site by using predefined package
        name
        """

        self._apply_info_common01(pkg_client, const)

        path = wayround_org.utils.path.abspath(self.path)

        ret = 0

        self.set_pkg_main_tarball('')

        if self.read_package_info(None) is None:
            logging.info(
                "Applying new package info to dir `{}'".format(
                    wayround_org.utils.path.abspath(
                        path
                        )
                    )
                )

            self.write_package_info({})

        if self.apply_constitution_on_buildingsite(const) != 0:
            ret = 2
        elif self.apply_pkg_info_on_buildingsite(
                pkg_client,
                package_name=package_name
                ) != 0:
            ret = 3
        else:
            # no error
            pass

        return ret

    apply_info.__doc__ += APPLY_DESCR

    def _complete_info_correctness_check(self):

        ret = 0

        r = self.read_package_info({})

        scr_name = ''

        try:
            scr_name = r['pkg_info']['buildscript']
        except:
            scr_name = ''

        if scr_name == '':
            ret = 1

        return ret

    def complete(
            self,
            build_ctl,
            pack_ctl,
            buildscript_ctl,
            pkg_client,
            main_src_file=None,
            const=None,
            remove_buildingsite_after_success=False,
            ):
        """
        Applies package information on building site, does building and
        packaging and optionally deletes building site after everything is
        done.

        :param main_src_file: used with function
            :func:`buildingsite.apply_info
            <wayround_org.aipsetup.buildingsite.apply_info>`
        """

        if not isinstance(const, Constitution):
            raise ValueError(
                "const must be of type "
                "wayround_org.aipsetup.build.Constitution"
                )

        if not isinstance(build_ctl, BuildCtl):
            raise ValueError(
                "build_ctl must be of type "
                "wayround_org.aipsetup.build.BuildCtl"
                )

        if not isinstance(pack_ctl, PackCtl):
            raise ValueError(
                "pack_ctl must be of type wayround_org.aipsetup.build.PackCtl"
                )

        if not isinstance(buildscript_ctl, BuildScriptCtrl):
            raise ValueError(
                "buildscript_ctl must be of type "
                "wayround_org.aipsetup.build.BuildScriptCtrl"
                )

        if not isinstance(
                pkg_client,
                wayround_org.aipsetup.client_pkg.PackageServerClient
                ):
            raise TypeError(
                "pkg_client must be of type "
                "wayround_org.aipsetup.client_pkg.PackageServerClient"
                )

        rp = wayround_org.utils.path.relpath(self.path, os.getcwd())

        logging.info(
            "+++++++++++ Starting Complete build under `{}' +++++++++++".
            format(rp)
            )

        building_site = wayround_org.utils.path.abspath(self.path)

        ret = 0

        """
        if (self._complete_info_correctness_check() != 0
                or isinstance(main_src_file, str)):

            logging.warning(
                "buildscript information not available "
                "(or new main tarball file forced)"
                )

            if self.apply_info(pkg_client, const, main_src_file) != 0:
                logging.error("Can't apply build information to site")
                ret = 15
        """

        if self.apply_info(pkg_client, const, main_src_file) != 0:
            logging.error("Can't apply build information to site")
            ret = 15

        if ret == 0:
            if self._complete_info_correctness_check() != 0:

                logging.error(
                    "`{}' has wrong build module name".format(main_src_file)
                    )
                ret = 16

        if ret == 0:

            log = wayround_org.utils.log.Log(
                self.getDIR_BUILD_LOGS(),
                'buildingsite complete'
                )
            log.info("Buildingsite processes started")
            log.warning("Closing this log now, cause it can't work farther")
            # log.stop()
            del log

            if build_ctl.complete(buildscript_ctl) != 0:
                logging.error("Error on building stage")
                ret = 1
            elif pack_ctl.complete() != 0:
                logging.error("Error on packaging stage")
                ret = 2

        if ret == 0:
            if remove_buildingsite_after_success:
                logging.info("Removing buildingsite after successful build")
                try:
                    shutil.rmtree(building_site)
                except:
                    logging.exception(
                        "Could not remove `{}'".format(building_site)
                        )

        logging.info(
            "+++++++++++ Finished Complete build under `{}' +++++++++++".
            format(rp)
            )

        return ret


def getDIR_x(path, x='TARBALL'):
    '''
    Returns absolute path to DIR_{_x}
    '''

    ret = wayround_org.utils.path.abspath(
        wayround_org.utils.path.join(
            path,
            eval('DIR_{}'.format(x))
            )
        )

    return ret


def getDIR_TARBALL(path):
    return getDIR_x(path, 'TARBALL')


def getDIR_SOURCE(path):
    return getDIR_x(path, 'SOURCE')


def getDIR_PATCHES(path):
    return getDIR_x(path, 'PATCHES')


def getDIR_BUILDING(path):
    return getDIR_x(path, 'BUILDING')


def getDIR_DESTDIR(path):
    return getDIR_x(path, 'DESTDIR')


def getDIR_BUILD_LOGS(path):
    return getDIR_x(path, 'BUILD_LOGS')


def getDIR_LISTS(path):
    return getDIR_x(path, 'LISTS')


def getDIR_TEMP(path):
    return getDIR_x(path, 'TEMP')


def build_script_wrap(buildingsite, desired_actions, action, help_text):
    """
    Used by building scripts for parsing action command

    :param buildingsite: path to building site
    :param desired_actions: list of possible actions
    :param action: action selected by building script user
    :param help_text: if action == 'help', help_text is text to show before
        list of available actions
    :rtype: ``int`` if error. ``tuple`` (package_info, actions), where
        ``package_info`` is package info readen from building site package info
        file, ``actions`` - list of actions, needed to be run by building
        script
    """

    bs = BuildingSiteCtl(buildingsite)

    pkg_info = bs.read_package_info()

    ret = 0

    if not isinstance(pkg_info, dict):
        logging.error("Can't read package info")
        ret = 1
    else:

        actions = copy.copy(desired_actions)

        if action == 'help':
            print(help_text)
            print("")
            print("Available actions: {}".format(actions))
            ret = 2
        else:

            r = build_actions_selector(
                actions,
                action
                )

            if not isinstance(r, tuple):
                logging.error("Wrong command 1")
                ret = 2
            else:

                actions, action = r

                if action is not None and not isinstance(action, str):
                    logging.error("Wrong command 2")
                    ret = 3
                else:

                    if not isinstance(actions, list):
                        logging.error("Wrong command 3")
                        ret = 3

                    else:

                        ret = (pkg_info, actions)

    return ret


def build_actions_selector(actions, action):
    """
    Used by :func:`build_script_wrap` to build it's valid return action list

    :rtype: ``None`` if error.
        tuple (actions, action), where ``action = None``
        if ``action == 'complete'``.

        If ``action == 'help'``, both values returned without changes.

        If action is one of actions, ``actions = [action]``.

        If action is one of actions and action ends with + sign,
        ``actions = actions[(action position):]``
    """

    ret = None

    actions = copy.copy(actions)

    if action == 'complete':
        action = None

    # action == None - indicates all actions! equals to 'complete'
    if action in [None, 'help']:
        ret = (actions, action)

    else:

        continued_action = True

        if isinstance(action, str) and action.endswith('+'):

            continued_action = True
            action = action[:-1]

        else:
            continued_action = False

        # if not action available - return error
        if action not in actions:

            ret = 2

        else:

            action_pos = actions.index(action)

            if continued_action:
                actions = actions[action_pos:]
            else:
                actions = [actions[action_pos]]

            ret = (actions, action)

    return ret


def isWdDirRestricted(path):
    """
    This function is a routine to check supplied path is it suitable to be a
    building site.

    List of forbidden path beginnings::

        [
        '/bin', '/boot' , '/daemons',
        '/dev', '/etc', '/lib', '/proc',
        '/sbin', '/sys',
        '/usr'
        ]

    This dirs ar directly forbidden, but subdirs are allowed::

        ['/opt', '/var', '/']

    :param path: path to directory
    :rtype: ``True`` if restricted. ``False`` if not restricted.
    """

    ret = False

    dirs_begining_with = [
        '/bin', '/boot', '/daemons',
        '/dev', '/etc', '/lib', '/proc',
        '/sbin', '/sys',
        '/usr'
        ]

    exec_dirs = ['/opt', '/var', '/']

    dir_str_abs = wayround_org.utils.path.abspath(path)

    for i in dirs_begining_with:
        if dir_str_abs.startswith(i):
            ret = True
            break

    if not ret:
        for i in exec_dirs:
            if i == dir_str_abs:
                ret = True
                break
    return ret


def find_dl(root_dir_path):

    ret = None

    raise Exception("deprecated")

    # TODO: better decigen required.

    if root_dir_path == '/multiarch/i686-pc-linux-gnu':
        ret = '/multiarch/i686-pc-linux-gnu/lib/ld-linux.so.2'

    elif root_dir_path == '/multiarch/x86_64-pc-linux-gnu':
        ret = '/multiarch/x86_64-pc-linux-gnu/lib/ld-linux-x86-64.so.2'

    else:

        root_dir_path = os.path.abspath(root_dir_path)

        gr = glob.glob(
            wayround_org.utils.path.join(
                root_dir_path,
                'lib',
                'ld-linux*.so.2'))

        if len(gr) == 1:
            ret = gr[0]

    return ret
