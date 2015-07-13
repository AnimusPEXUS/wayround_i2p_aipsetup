
import collections

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()

        lst = list(ret.items())

        index = -1
        for i in range(len(lst)):

            if lst[i][0] == 'build':
                index = i
                break

        if index == -1:
            raise Exception("Programming error")

        lst.insert(index + 1, ('build2', self.builder_action_build2))
        lst.insert(index + 1, ('distribute2', self.builder_action_distribute2))

        ret = collections.OrderedDict(lst)

        return ret

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--with-x',
            '--with-install-cups',
            ]

    def builder_action_build2(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['so'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute2(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'soinstall',
                'DESTDIR={}'.format(self.dst_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
