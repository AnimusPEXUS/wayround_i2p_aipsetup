
import glob
import os.path
import json
import yaml

files = glob.glob('*.gpl.yaml')

for i in files:

    os.rename(i, i[:-5])
