#!/bin/bash

# do `emacs --daemon` before starting this script
find . -maxdepth 2 -name '*.py' -exec bash -c 'emacsclient -c -n {} &' ';'
find ./templates -maxdepth 1 -name '*.html' -exec bash -c 'emacsclient -c -n {} &' ';'
