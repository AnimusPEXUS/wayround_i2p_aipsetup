
import glob
import os.path
import json
import yaml

files = glob.glob('*.gpl')

for i in files:

    with open(i) as f:
        txt = f.read()

    data = json.loads(txt)

    with open(i + '.yaml', 'w') as f:
        f.write(yaml.dump(data))
