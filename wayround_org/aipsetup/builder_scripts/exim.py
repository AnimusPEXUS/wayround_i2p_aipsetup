
import os.path
import shutil
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required
# TODO: try to set parameters to make, - without editing config file
# TODO: looks like already most of all this file need to be rewrited


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {}

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('fix_exim_install', self.builder_action_fix_exim_install),
            ('config_exim', self.builder_action_config_exim),
            ('config_eximon', self.builder_action_config_eximon),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute),
            ('rename_configs', self.builder_action_rename_configs),
            ('sendmail_link', self.builder_action_sendmail_link)
            ])

    def builder_action_fix_exim_install(self, called_as, log):

        exim_install = wayround_org.utils.path.join(
            self.get_src_dir(),
            'scripts',
            'exim_install'
            )

        f = open(exim_install, 'r')
        ft = f.read()
        f.close()

        ftl = ft.splitlines()

        for i in range(len(ftl)):
            if ftl[i].startswith('do_chown=yes'):
                log.info('edit: do_chown=yes to do_chown=no')
                ftl[i] = 'do_chown=no'

        ft = '\n'.join(ftl)
        f = open(exim_install, 'w')
        ft = f.write(ft)
        f.close()

        return 0

    def builder_action_config_exim(self, called_as, log):

        ret = 0

        editme = wayround_org.utils.path.join(
            self.get_src_dir(),
            'src',
            'EDITME'
            )
        editme_makefile = wayround_org.utils.path.join(
            self.get_src_dir(),
            'Local',
            'Makefile'
            )

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
                    log.info("edit: '{}'".format(ftl[i]))
                    ftl[i] = 'BIN_DIRECTORY={}/bin'.format(
                        self.calculate_install_prefix()
                        )

                if ftl[i].startswith('CONFIGURE_FILE=/usr/exim/configure'):
                    log.info("edit: '{}'".format(ftl[i]))
                    ftl[i] = 'CONFIGURE_FILE=/etc/exim/configure'

                if ftl[i].startswith('EXIM_USER='):
                    log.info("edit: '{}'".format(ftl[i]))
                    ftl[i] = 'EXIM_USER=ref:exim'

                if ftl[i].startswith('# EXIM_GROUP='):
                    log.info("edit: '{}'".format(ftl[i]))
                    # TODO: question: 'exim' or 'mail' group? as exim it self
                    #       has exim:exim rights
                    ftl[i] = 'EXIM_GROUP=ref:exim'

                for j in [
                    # '# LOOKUP_CDB=yes',
                    # '# LOOKUP_DSEARCH=yes',
                    # '# LOOKUP_IBASE=yes',

                    # '# LOOKUP_LDAP=yes',
                    # '# LDAP_LIB_TYPE=OPENLDAP2',

                    # '# LOOKUP_MYSQL=yes',
                    # '# LOOKUP_NIS=yes',
                    # '# LOOKUP_NISPLUS=yes',
                    # '# LOOKUP_ORACLE=yes',
                    # '# LOOKUP_PASSWD=yes',
                    # '# LOOKUP_PGSQL=yes',
                    # '# LOOKUP_SQLITE=yes',
                    # '# LOOKUP_SQLITE_PC=sqlite3',
                    # '# LOOKUP_WHOSON=yes',
                    '# SUPPORT_MAILDIR=yes',
                    '# SUPPORT_MAILSTORE=yes',
                    '# SUPPORT_MBX=yes',

                    '# AUTH_CRAM_MD5=yes',
                    '# AUTH_CYRUS_SASL=yes',
                    '# AUTH_DOVECOT=yes',
                    '# AUTH_GSASL=yes',
                    '# AUTH_GSASL_PC=libgsasl',
                    # '# AUTH_HEIMDAL_GSSAPI=yes',
                    # '# AUTH_HEIMDAL_GSSAPI_PC=heimdal-gssapi',
                    '# AUTH_PLAINTEXT=yes',
                    '# AUTH_SPA=yes',
                    # '# AUTH_LIBS=-lsasl2',
                    # '# AUTH_LIBS=-lgsasl',
                    # '# AUTH_LIBS=-lgssapi -lheimntlm -lkrb5 -lhx509 '
                    #                          '-lcom_err -lhcrypto -lasn1 -lwind -lroken -lcrypt',

                    '# HAVE_ICONV=yes',
                    '# SUPPORT_TLS=yes',

                    '# USE_OPENSSL_PC=openssl',
                    # '# TLS_LIBS=-lssl -lcrypto',

                    # '# TLS_LIBS=-L/usr/local/openssl/lib -lssl -lcrypto',

                    # '# USE_GNUTLS=yes',
                    # '# USE_GNUTLS_PC=gnutls',
                    # '# TLS_LIBS=-lgnutls -ltasn1 -lgcrypt'

                        '# WITH_CONTENT_SCAN=yes',
                        '# SUPPORT_PAM=yes',
                        ]:

                    if ftl[i].startswith(j):
                        log.info("edit: '{}' to '{}'".format(ftl[i], j[2:]))
                        ftl[i] = j[2:]

                if ftl[i].startswith(
                        '# AUTH_LIBS=-lgssapi -lheimntlm -lkrb5 -lhx509 '
                        '-lcom_err -lhcrypto -lasn1 -lwind -lroken -lcrypt'
                        ):

                    log.info("edit: '{}'".format(ftl[i]))

                    ftl.insert(i + 1, 'AUTH_LIBS=-lsasl2 -lgsasl')

            ftl.append('EXTRALIBS+=-lpam')

            if ret == 0:

                ft = '\n'.join(ftl)
                f = open(editme_makefile, 'w')
                ft = f.write(ft)
                f.close()

                ret = 0
        return ret

    def builder_action_config_eximon(self, called_as, log):
        editme_mon = wayround_org.utils.path.join(
            self.get_src_dir(),
            'exim_monitor',
            'EDITME'
            )
        editme_makefile_mon = \
            wayround_org.utils.path.join(
                self.get_src_dir(),
                'Local',
                'eximon.conf'
                )

        shutil.copy(editme_mon, editme_makefile_mon)
        return 0

    def builder_action_rename_configs(self, called_as, log):
        for i in [
                wayround_org.utils.path.join(
                    self.get_dst_dir(),
                    'etc',
                    'exim',
                    'configure'
                    ),
                wayround_org.utils.path.join(
                    self.get_dst_dir(),
                    'etc',
                    'aliases'
                    )
                ]:

            if os.path.exists(i):
                log.info("rename: '{}' to '{}'".format(i, i + '.example'))
                shutil.move(i, i + '.example')
        return 0

    def builder_action_sendmail_link(self, called_as, log):
        lnk = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'bin',
            'sendmail'
            )

        if os.path.exists(lnk) or os.path.islink(lnk):
            os.unlink(lnk)

        lnk_dir = os.path.dirname(lnk)
        os.makedirs(lnk_dir, exist_ok=True)

        log.info("link: '{}'".format(lnk))
        os.symlink('./exim', lnk)
        return 0
