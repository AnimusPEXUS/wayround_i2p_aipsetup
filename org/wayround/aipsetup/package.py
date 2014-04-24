
"""
Module for GNU/Linux system related package actions
"""

import logging
import os.path
import tarfile

import org.wayround.utils.archive
import org.wayround.utils.checksum
import org.wayround.utils.path


class ASPackage:

    """
    Not installed package file actions
    """

    def __init__(self, asp_filename):

        self.filename = org.wayround.utils.path.abspath(asp_filename)

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
                    f = org.wayround.utils.archive.tar_member_get_extract_file(
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
                            org.wayround.utils.checksum.parse_checksums_text(
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
                                or org.wayround.utils.archive.\
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

                            fobj = org.wayround.utils.archive.\
                                tar_member_get_extract_file(
                                    tarf,
                                    './06.LISTS/DESTDIR.lst.xz'
                                    )
                            if not isinstance(fobj, tarfile.ExFileObject):
                                ret = False
                            else:

                                try:
                                    dest_dir_files_list = \
                                        org.wayround.utils.archive.xzcat(
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
                                    os.path.basename(self.filename),
                                    p1
                                    )
                                                    )
                                                ret = 5
                                                break

                                            elif j == p2:
                                                logging.error(
                                "{} has file paths equal to {}".format(
                                    os.path.basename(self.filename),
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

    def check_package_aipsetup2(self):
        """
        Check aipsetup v2 package consistency

        :rtype: ``0`` - if no errors.
        """

        ret = 0

        if not self.filename.endswith('.tar.xz'):
            ret = 1
        else:
            filename_sha512 = self.filename + '.sha512'
            filename_md5 = self.filename + '.md5'

            if (not os.path.isfile(self.filename)
                or not os.path.isfile(filename_sha512)
                or not os.path.isfile(filename_md5)
                ):
                ret = 2
            else:

                bn = os.path.basename(self.filename)
                dbn = './' + bn

                sha512 = org.wayround.utils.checksum.make_file_checksum(
                    self.filename, 'sha512'
                    )

                md5 = org.wayround.utils.checksum.make_file_checksum(
                    self.filename, 'md5'
                    )

                sha512s = \
                    org.wayround.utils.checksum.parse_checksums_file_text(
                        filename_sha512
                        )

                md5s = org.wayround.utils.checksum.parse_checksums_file_text(
                    filename_md5
                    )

                if not isinstance(sha512, str):
                    ret = 3
                elif not isinstance(md5, str):
                    ret = 4
                elif not isinstance(sha512s, dict):
                    ret = 5
                elif not isinstance(md5s, dict):
                    ret = 6
                elif not dbn in sha512s:
                    ret = 7
                elif not dbn in md5s:
                    ret = 8
                elif not sha512s[dbn] == sha512:
                    ret = 9
                elif not md5s[dbn] == md5:
                    ret = 10
                else:
                    ret = 0

        return ret
