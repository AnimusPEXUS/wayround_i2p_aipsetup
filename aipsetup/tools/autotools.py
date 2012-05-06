import os.path
import subprocess
import glob
import shutil

import aipsetup.extractor
import aipsetup.buildingsite
# import aipsetup.name


def extract(config, buildingsite='.'):
    tarball_dir = os.path.join(
        buildingsite,
        aipsetup.buildingsite.DIR_TARBALL
        )

    output_dir = os.path.join(
        buildingsite,
        aipsetup.buildingsite.DIR_SOURCE
        )

    arch = glob.glob(os.path.join(tarball_dir, '*'))
    if len(arch) == 0:
        print "-e- No tarballs supplied"
    elif len(arch) > 1:
        print "-e- autotools[configurer]: too many source files"
    else:

        arch = arch[0]

        arch_bn = os.path.basename(arch)

        aipsetup.extractor.extract(arch, output_dir)

        extracted_dir = glob.glob(os.path.join(output_dir, '*'))

        if len(extracted_dir) > 1:
            print "-e- autotools[configurer]: too many extracted files"
        else:
            extracted_dir = extracted_dir[0]
            extracted_dir_files = glob.glob(os.path.join(extracted_dir, '*'))
            for i in extracted_dir_files:
                shutil.move(i, output_dir)
            shutil.rmtree(extracted_dir)

    return


def configure(options, build_dir, run_dir):
    pass
