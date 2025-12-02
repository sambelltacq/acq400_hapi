#!/usr/bin/env python3

"""
Set run0 value

Usage:
    ./user_apps/acq400/acq400_run0.py 1,2 acq2106_000
    ./user_apps/acq400/acq400_run0.py 1,2 1,8,0 acq2106_000
"""

import argparse
from acq400_hapi import factory

def run_main(args):
    uut = factory(args.uutname)
    if args.spad: uut.s0.spad = args.spad
    run_str = "{} {}".format(args.sites, uut.s0.spad)
    uut.s0.run0 = run_str
    print(f"{args.uutname} run0 {run_str}")

def get_parser():
    parser = argparse.ArgumentParser(description='Set run0 on UUT')
    parser.add_argument('sites', help="sites value")
    parser.add_argument('spad', nargs='?', help="spad value")
    parser.add_argument('uutname', help="uutname")
    return parser

if __name__ == '__main__':
    run_main(get_parser().parse_args())
