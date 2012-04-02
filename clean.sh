#!/bin/bash

find .   '(' -name '*~' -o -name '*#*' -o -name '*.pyc' -o -name '*.pyo' ')' -exec rm '{}' ';'

rm -r html
bash gen_api_doc.sh

chmod -R u=rwx .
