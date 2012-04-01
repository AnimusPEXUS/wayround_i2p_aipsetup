import subprocess
import aipsetup.extractor

def extract(file_name, output_dir):
    aipsetup.extractor.extract(file_name, output_dir)


def configure(options, build_dir, run_dir):
    pass
