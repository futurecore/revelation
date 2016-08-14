#!/usr/bin/env python

import subprocess

def get_version_string():
    tags = subprocess.check_output(['git', 'tag'])
    if tags:
        tag_list = sorted(tags.strip().split('\n'))
        return tag_list[-1]
    return 'pre-release'

def get_minor_version_string():
    return '.'.join(get_version_string().split('.')[:2])

if __name__ == '__main__':
    print get_minor_version_string()
