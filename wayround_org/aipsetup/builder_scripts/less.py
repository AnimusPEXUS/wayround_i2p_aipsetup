
import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def define_custom_data(self):
        etc_profile_set_dir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'etc',
            'profile.d',
            'SET'
            )

        ret = {
            'etc_profile_set_dir': etc_profile_set_dir
            }

        return ret

    def builder_action_after_distribute(self, called_as, log):

        os.makedirs(self.custom_data['etc_profile_set_dir'], exist_ok=True)

        f = open(
            wayround_org.utils.path.join(
                self.custom_data['etc_profile_set_dir'],
                '009.LESS.sh'
                ),
            'w'
            )

        f.write("""\
#!/bin/bash
export LESS=' -R '

""")
        f.close()

        return 0
