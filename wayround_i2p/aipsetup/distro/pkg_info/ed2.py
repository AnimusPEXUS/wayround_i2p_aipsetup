
import os
import json

lstd = []

lst = os.listdir()

for i in lst:

    if i.endswith('.json'):

        with open(i) as f:
            if '0246' in f.read():
                lstd.append(i[:-5])



with open('list_of_gnome_versions.json', 'w') as f:
    f.write(json.dumps(sorted(lstd)))
