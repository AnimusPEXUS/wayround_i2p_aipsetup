

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        ret['pc'] = self.builder_action_pc
        return ret

    def builder_action_build_define_args(self, called_as, log):
        return [
            'linux',
            'INSTALL_TOP={}'.format(self.calculate_install_prefix()),
            'MYCFLAGS=-std=gnu99',
            'MYLDFLAGS=-ltinfow'
            ] + self.all_automatic_flags_as_list()

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'INSTALL_TOP={}'.format(self.calculate_dst_install_prefix()),
            'MYCFLAGS=-std=gnu99',
            'MYLDFLAGS=-ltinfow'
            ] + self.all_automatic_flags_as_list(),

    def builder_action_pc(self, called_as, log):

        libdir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'lib'
            )

        if not os.path.isdir(libdir):
            libdir = wayround_org.utils.path.join(
                self.calculate_dst_install_prefix(),
                'lib64'
                )

        if not os.path.isdir(libdir):
            raise Exception("Can't calculate libdir")

        pc_file_name_dir = wayround_org.utils.path.join(
            libdir,
            'pkgconfig'
            )

        os.makedirs(
            pc_file_name_dir,
            exist_ok=True
            )

        pc_file_name = wayround_org.utils.path.join(
            pc_file_name_dir,
            'lua.pc'
            )

        pc_file = open(pc_file_name, 'w')

        pc_text = ''

        p = subprocess.Popen(
            ['make',
             'pc',
             'INSTALL_TOP={}'.format(self.calculate_dst_install_prefix())
             ],
            stdout=subprocess.PIPE,
            cwd=self.get_src_dir()
            )
        p.wait()
        pc_text = p.communicate()[0]
        pc_text = str(pc_text, 'utf-8')
        pc_lines = pc_text.splitlines()

        version = []

        for i in pc_lines:
            if i.startswith('version='):
                version = i.split('=')[1].split('.')

        tpl = """\
V={V}
R={R}

prefix={arch_path}
INSTALL_BIN=${{prefix}}/bin
INSTALL_INC=${{prefix}}/include
INSTALL_LIB=${{prefix}}/{lib_dir_name}
INSTALL_MAN=${{prefix}}/man/man1
INSTALL_LMOD=${{prefix}}/share/lua/${{V}}
INSTALL_CMOD=${{prefix}}/{lib_dir_name}/lua/${{V}}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/{lib_dir_name}
includedir=${{prefix}}/include

Name: Lua
Description: An Extensible Extension Language
Version: ${{R}}
Requires:
Libs: -L${{libdir}} -llua -lm
Cflags: -I${{includedir}}
""".format(
            V='.'.join(version[:2]),
            R='.'.join(version),
            arch_path='{}'.format(self.calculate_install_prefix()),
            os.path.relpath(
                self.calculate_install_libdir(),
                self.calculate_install_prefix()
                )
            )

        pc_file.write(tpl)
        pc_file.close()
        return 0
