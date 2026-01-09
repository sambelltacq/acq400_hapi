#!/usr/bin/env python
"""
run a dio2stl process

usage: run_dio2stl.py [-h] uut

run_dio2stl

positional arguments:
  uut                   uut

optional arguments:
  -h, --help            show this help message and exit
"""

import acq400_hapi
import argparse


def run_shot(args):
    uut = acq400_hapi.Acq400(args.uuts[0])
    acq400_hapi.cleanup.init()
    uut.run_dio2stl()
    

def run_main():
    parser = argparse.ArgumentParser(description='dio2stl demo')
    parser.add_argument('uuts', nargs=1, help="uut ")
    run_shot(parser.parse_args())


if __name__ == '__main__':
    run_main()


