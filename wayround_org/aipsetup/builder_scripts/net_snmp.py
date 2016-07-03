

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-defaults',

            # NOTE: error otherways
            #       new error discovered:
            #
            # ../include/net-snmp/library/int64.h:8:30: error: conflicting types for 'U64'
            #      typedef struct counter64 U64;
            #                               ^
            #  In file included from /multihost/x86_64-pc-linux-gnu/lib/perl5/5.24.0/x86_64-linux/CORE/perl.h:2684:0,
            #                  from snmp_perl.c:6:
            # /multihost/x86_64-pc-linux-gnu/lib/perl5/5.24.0/x86_64-linux/CORE/handy.h:179:17: note: previous declaration of 'U64' was here
            #  typedef U64TYPE U64;
            #                  ^

            '--disable-embedded-perl'
            ]

    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1
