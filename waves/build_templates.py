#!/usr/bin/env python3
# encoding: utf-8
'''
waves.build_templates -- shortdesc

'''

import sys
import os
import argparse
import re

import templates.all_templates

root_prefix = os.getenv("AWG_TEMPLATE_ROOT", "/tmp/AWG")

line = 0
files = []

def process(cmd):
    global line
    global files
    print(f"process {line}")
    line += 1
    if not cmd or len(cmd[0]) == 0:
        return -1
    elif cmd[0] == '#':
        return 0
    
    print(f"process {cmd}")

    match = re.search(r'([A-Za-z0-9_-]+)/([0-9]+)', cmd[0])
    if match:
        root = f'{root_prefix}/{match.group(1)}'
        chan = match.group(2)
        cmd = cmd[1:]
        cmd.extend(('--root', root, '--ch', chan))
        print(cmd)
        
    wave_commands = templates.all_templates.get_wave_commands()
    for key in sorted(wave_commands.keys()):
        if cmd[0] == key:
            print(f"DEBUG: {key} {cmd}")
            data, fn = wave_commands[key](cmd[1:])
            if data is not None and fn is not None:
                print(f'DEBUG: fn:{fn} data_len:{len(data)}')
                files.append((fn, len(data)))
            return 0
        
    print(f'[{line}] ERROR cmd {" ".join(cmd)} cmd not found')
    return 0

def main():
    global files
    
    try:
        while process(input(">").split()) >= 0:
            pass
    except EOFError:
        print("EOF")

    manifest = f'{root_prefix}/MANIFEST'
    with open(manifest, "w") as fp:
        for ii, fnl in enumerate(files):
            fn, fl = fnl
            seg, fn_base = fn[len(root_prefix)+1:].split('/')
            ch, ext = fn_base.split('_')[-1].split('.')
        
            fp.write(f'{ii} {fn} {fl} {seg} {ch} {fn_base}\n')
    print(f'FINISHED {manifest}')

         

if __name__ == "__main__":
    sys.exit(main())