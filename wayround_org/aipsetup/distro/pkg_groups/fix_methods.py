
import os
import json
import logging
import collections

lst = os.listdir()

groups = {}

for i in lst:

    if i.endswith('.gpl') or i.endswith('.json'):

        try:
            with open(i) as f:
                groups[i] = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)
        except:
            logging.exception("Can't read: {}".format(i))

gnome_versions = groups['gnome_versions.gpl']
list_of_gnome_versions = groups['list_of_gnome_versions.json']
del groups['gnome_versions.gpl']
del groups['list_of_gnome_versions.json']

#exit(0)

for lgv in list_of_gnome_versions:

    lgv_found = False
    
    for group in list(groups.keys()):

        group_names = groups[group]['names']

        if isinstance(group_names, dict):

            for group_name in list(group_names.keys()):

                if group_name == lgv:

                    lgv_found = True
                    group_names[group_name]['proc'] = 'gnome_get'

        elif type(group_names) == list:

            for group_name in list(group_names):

                if type(group_name) == str:

                    if group_name == lgv:
                        lgv_found = True
                        group_names.remove(group_name)
                        group_names.append(
                            {'name': group_name, 'proc': 'gnome_get'}
                        )

                elif isinstance(group_name, dict):
                    group_name_name = group_name['name']
                    if group_name_name == lgv:
                        lgv_found = True
                        group_name['proc'] = 'gnome_get'

                else:
                    raise ValueError("error")


        else:
            raise ValueError("error")

    if not lgv_found:
        group_names = gnome_versions['names']
        lgv_found2 = False
        for group_name in list(group_names):

            if type(group_name) == str:

                if group_name == lgv:
                    lgv_found2 = True
                    group_names.remove(group_name)
                    group_names.append(
                        {'name': group_name, 'proc': 'gnome_get'}
                    )

            elif type(group_name) == dict:
                group_name_name = group_name['name']
                if group_name_name == lgv:
                    lgv_found2 = True
                    group_name['proc'] = 'gnome_get'

            else:
                raise ValueError("error")
                    
        if not lgv_found2:
            group_names.append(
                {'name': lgv, 'proc': 'gnome_get'}
            )
        
        
for group in list(groups.keys()):

    with open(group, 'w') as f:
        f.write(json.dumps(groups[group], indent=4))


with open('gnome_versions.gpl', 'w') as f:
    f.write(json.dumps(gnome_versions, indent=4))
