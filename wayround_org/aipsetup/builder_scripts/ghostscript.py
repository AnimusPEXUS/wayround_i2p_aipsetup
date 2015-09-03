
import collections

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()

        del ret['build']
        # lst = list(ret.items())

        # index = -1
        # for i in range(len(lst)):

        #     if lst[i][0] == 'build':
        #         index = i
        #         break

        # if index == -1:
        #     raise Exception("Programming error")

        #lst.insert(index + 1, ('build2', self.builder_action_build2))
        #lst.insert(index + 1, ('distribute2', self.builder_action_distribute2))

        #ret = collections.OrderedDict(lst)

        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-x',
            '--with-install-cups',
            '--with-ijs',
            '--with-drivers=ALL',
            #'SHARE_IJS=1'
            ]

    # def builder_action_build_define_args(self, called_as, log):
    #     return [
    #         , #'SHARE_IJS=1'
    #         ]

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'all',
            'install',
            'so',
            'soinstall',
            'DESTDIR={}'.format(self.get_dst_dir()),
            #'SHARE_IJS=1'
            ]
