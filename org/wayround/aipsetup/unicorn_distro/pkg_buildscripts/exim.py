
import logging
import os.path
import shutil

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'fix_exim_install', 'config_exim',
         'config_eximon', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        editme = os.path.join(src_dir, 'src', 'EDITME')

        editme_makefile = os.path.join(src_dir, 'Local', 'Makefile')

        editme_mon = os.path.join(src_dir, 'exim_monitor', 'EDITME')

        editme_makefile_mon = os.path.join(src_dir, 'Local', 'eximon.conf')

        exim_install = os.path.join(src_dir, 'scripts', 'exim_install')

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'fix_exim_install' in actions and ret == 0:
            f = open(exim_install, 'r')
            ft = f.read()
            f.close()

            ftl = ft.splitlines()

            for i in range(len(ftl)):
                if ftl[i].startswith('do_chown=yes'):
                    ftl[i] = 'do_chown=no'

            ft = '\n'.join(ftl)
            f = open(exim_install, 'w')
            ft = f.write(ft)
            f.close()

        if 'config_exim' in actions and ret == 0:

            try:
                shutil.copy(editme, editme_makefile)
            except:
                ret = 1
            else:
                f = open(editme_makefile, 'r')
                ft = f.read()
                f.close()

                ftl = ft.splitlines()

                for i in range(len(ftl)):

                    if ftl[i].startswith('BIN_DIRECTORY=/usr/exim/bin'):
                        ftl[i] = 'BIN_DIRECTORY=/usr/bin'

                    if ftl[i].startswith('CONFIGURE_FILE=/usr/exim/configure'):
                        ftl[i] = 'CONFIGURE_FILE=/etc/exim/configure'

                    if ftl[i].startswith('EXIM_USER='):
                        ftl[i] = 'EXIM_USER=ref:exim'

                    if ftl[i].startswith('# EXIM_GROUP='):
                        ftl[i] = 'EXIM_GROUP=ref:exim'

                    for j in [
#                        '# LOOKUP_CDB=yes',
#                        '# LOOKUP_DSEARCH=yes',
#                        '# LOOKUP_IBASE=yes',

#                        '# LOOKUP_LDAP=yes',
#                        '# LDAP_LIB_TYPE=OPENLDAP2',

#                        '# LOOKUP_MYSQL=yes',
#                        '# LOOKUP_NIS=yes',
#                        '# LOOKUP_NISPLUS=yes',
#                        '# LOOKUP_ORACLE=yes',
#                        '# LOOKUP_PASSWD=yes',
#                        '# LOOKUP_PGSQL=yes',
#                        '# LOOKUP_SQLITE=yes',
#                        '# LOOKUP_SQLITE_PC=sqlite3',
#                        '# LOOKUP_WHOSON=yes',
                        '# SUPPORT_MAILDIR=yes',
                        '# SUPPORT_MAILSTORE=yes',
                        '# SUPPORT_MBX=yes',

                        '# AUTH_CRAM_MD5=yes',
                        '# AUTH_CYRUS_SASL=yes',
                        '# AUTH_DOVECOT=yes',
                        '# AUTH_GSASL=yes',
                        '# AUTH_GSASL_PC=libgsasl',
#                        '# AUTH_HEIMDAL_GSSAPI=yes',
#                        '# AUTH_HEIMDAL_GSSAPI_PC=heimdal-gssapi',
                        '# AUTH_PLAINTEXT=yes',
                        '# AUTH_SPA=yes',
#                        '# AUTH_LIBS=-lsasl2',
#                        '# AUTH_LIBS=-lgsasl',
#                        '# AUTH_LIBS=-lgssapi -lheimntlm -lkrb5 -lhx509 '
#                          '-lcom_err -lhcrypto -lasn1 -lwind -lroken -lcrypt',

                        '# HAVE_ICONV=yes',
                        '# SUPPORT_TLS=yes',

                        '# USE_OPENSSL_PC=openssl',
#                        '# TLS_LIBS=-lssl -lcrypto',

#                        '# TLS_LIBS=-L/usr/local/openssl/lib -lssl -lcrypto',

#                        '# USE_GNUTLS=yes',
#                        '# USE_GNUTLS_PC=gnutls',
#                        '# TLS_LIBS=-lgnutls -ltasn1 -lgcrypt'

                        '# WITH_CONTENT_SCAN=yes',
                        '# SUPPORT_PAM=yes',
                        ]:

                        if ftl[i].startswith(j):
                            ftl[i] = j[2:]

                    if ftl[i].startswith(
                        '# AUTH_LIBS=-lgssapi -lheimntlm -lkrb5 -lhx509 '
                        '-lcom_err -lhcrypto -lasn1 -lwind -lroken -lcrypt'
                        ):

                        ftl.insert(i + 1, 'AUTH_LIBS=-lsasl2 -lgsasl')

                ftl.append('EXTRALIBS+=-lpam')

                if ret == 0:

                    ft = '\n'.join(ftl)
                    f = open(editme_makefile, 'w')
                    ft = f.write(ft)
                    f.close()

                    ret = 0

        if 'config_eximon' in actions and ret == 0:

            try:
                shutil.copy(editme_mon, editme_makefile_mon)
            except:
                ret = 1
            else:
                ret = 0

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            for i in [
                os.path.join(dst_dir, 'etc', 'exim', 'configure'),
                os.path.join(dst_dir, 'etc', 'aliases')
                ]:

                if os.path.exists(i):
                    shutil.move(
                        i,
                        i + '.example'
                        )

            lnk = os.path.join(dst_dir, 'usr', 'bin', 'sendmail')

            if os.path.exists(lnk) or os.path.islink(lnk):
                os.unlink(lnk)

            os.symlink('./exim', lnk)

    return ret
