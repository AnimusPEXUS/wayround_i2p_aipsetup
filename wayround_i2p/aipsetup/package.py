
"""
Module for GNU/Linux system related package actions
"""

import logging
import os.path
import tarfile

import wayround_org.utils.archive
import wayround_org.utils.checksum
import wayround_org.utils.path

import wayround_org.aipsetup.package_name_parser


class ASPackage:
    """
    Not installed package file actions
    """

    def __init__(self, asp_filename):
        self._filename = wayround_org.utils.path.abspath(asp_filename)
        self.parsed_name = \
            wayround_org.aipsetup.package_name_parser.package_name_parse(
                os.path.basename(self.filename)
                )
        return

    @property
    def filename(self):
        ret = None
        try:
            ret = self._filename
        except:
            ret = None
        return ret

    @property
    def host(self):
        ret = None
        try:
            ret = self.parsed_name['groups']['host']
        except:
            ret = None
        return ret

    @property
    def arch(self):
        ret = None
        try:
            ret = self.parsed_name['groups']['arch']
        except:
            ret = None
        return ret

    @property
    def status(self):
        ret = None
        try:
            ret = self.parsed_name['groups']['status']
        except:
            ret = None
        return ret

    @property
    def timestamp(self):
        ret = None
        try:
            ret = self.parsed_name['groups']['timestamp']
        except:
            ret = None
        return ret

    @property
    def timestamp_datetime(self):
        ret = None
        ts = self.timestamp
        if ts is not None:
            ret = wayround_org.aipsetup.package_name_parser.parse_timestamp(
                ts
                )
        return ret

    @property
    def name(self):
        ret = None
        try:
            ret = self.parsed_name['groups']['name']
        except:
            ret = None
        return ret

    def check_package(self, mute=False):
        """
        Check package for errors
        """
        ret = 0

        if not self.filename.endswith('.asp'):
            if not mute:
                logging.error(
                    "Wrong file extension `{}'".format(self.filename)
                    )
            ret = 3
        else:
            try:
                tarf = tarfile.open(self.filename, mode='r')
            except:
                logging.exception("Can't open file `{}'".format(self.filename))
                ret = 1
            else:
                try:
                    f = wayround_org.utils.archive.tar_member_get_extract_file(
                        tarf,
                        './package.sha512'
                        )
                    if not isinstance(f, tarfile.ExFileObject):
                        logging.error("Can't get checksums from package file")
                        ret = 2
                    else:
                        sums_txt = f.read()
                        f.close()
                        sums = \
                            wayround_org.utils.checksum.parse_checksums_text(
                                sums_txt
                                )
                        del(sums_txt)

                        sums2 = {}
                        for i in sums:
                            sums2['.' + i] = sums[i]
                        sums = sums2
                        del(sums2)

                        tar_members = tarf.getmembers()

                        check_list = [
                            './04.DESTDIR.tar.xz', './05.BUILD_LOGS.tar.xz',
                            './package_info.json', './02.PATCHES.tar.xz'
                            ]

                        for i in ['./00.TARBALL', './06.LISTS']:
                            for j in tar_members:
                                if (
                                        j.name.startswith(i)
                                        and j.name != i
                                        ):
                                    check_list.append(j.name)

                        check_list.sort()

                        error_found = False

                        for i in check_list:
                            cresult = ''
                            if (
                                    not i in sums
                                    or wayround_org.utils.archive.
                                tarobj_check_member_sum(
                                    tarf, sums, i
                                    ) == False
                                    ):
                                error_found = True
                                cresult = "FAIL"
                            else:
                                cresult = "OK"

                            if not mute:
                                print(
                                    "       {name} - {result}".format_map(
                                        {
                                            'name': i,
                                            'result': cresult
                                            }
                                        )
                                    )

                        if error_found:
                            logging.error(
                                "Error was found while checking package"
                                )
                            ret = 3
                        else:

                            # TODO: additionally to this leaf, make test
                            #       by tar -t output to privent installation of
                            #       broken DESTDIR

                            fobj = wayround_org.utils.archive.\
                                tar_member_get_extract_file(
                                    tarf,
                                    './06.LISTS/DESTDIR.lst.xz'
                                    )
                            if not isinstance(fobj, tarfile.ExFileObject):
                                ret = False
                            else:

                                try:
                                    dest_dir_files_list = \
                                        wayround_org.utils.archive.xzcat(
                                            fobj,
                                            convert_to_str='utf-8'
                                            )

                                    dest_dir_files_list = \
                                        dest_dir_files_list.splitlines()

                                    for i in [
                                            'bin',
                                            'sbin',
                                            'lib',
                                            'lib64'
                                            ]:

                                        for j in dest_dir_files_list:

                                            p1 = os.path.sep + i + os.path.sep
                                            p2 = os.path.sep + i

                                            if j.startswith(p1):
                                                logging.error(
                                                    "{} has file paths starting with {}".format(
                                                        os.path.basename(
                                                            self.filename),
                                                        p1
                                                        )
                                                    )
                                                ret = 5
                                                break

                                            elif j == p2:
                                                logging.error(
                                                    "{} has file paths equal to {}".format(
                                                        os.path.basename(
                                                            self.filename),
                                                        p2
                                                        )
                                                    )
                                                ret = 5
                                                break

                                            if ret != 0:
                                                break

                                except:
                                    logging.exception("Error")
                                    ret = 4
                                finally:
                                    fobj.close()
                finally:
                    tarf.close()

        return ret
