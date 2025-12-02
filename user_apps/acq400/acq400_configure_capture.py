#!/usr/bin/env python3

"""
Configure capture for UUTs

Usage:
    # Default Post
    ./user_apps/acq400/acq400_configure_capture.py --post=100K --trg=1,0,1 acq2106_000

    # Default PrePost
    ./user_apps/acq400/acq400_configure_capture.py --pre=50K --post=50K --trg=1,1,1 --event0=1,0,0 acq2106_000

    # Default RGM
    ./user_apps/acq400/acq400_configure_capture.py --post=100K --trg=1,1,1 --rgm=3,0,1 --translen=4096 acq2106_000

"""

import argparse
from acq400_hapi import factory, ArgTypes

def run_main(args):
    for uutname in args.uutnames:
        uut = factory(uutname)
        uut.configure_capture(
            pre=args.pre,
            post=args.post,
            soft=args.auto_soft,
            trigger=args.trg,
            event0=args.event0,
            event1=args.event1,
            rgm=args.rgm,
            spad=args.spad,
            translen=args.translen,
            demux=args.demux,
        )
        print("{} Config: {}".format(uutname, vars(args)))

def get_parser():
    parser = argparse.ArgumentParser(description='Configure Capture on muliple UUTs')
    parser.add_argument('--pre', default=0, type=ArgTypes.int_with_unit, help="Pre samples target")
    parser.add_argument('--post', default=0, type=ArgTypes.int_with_unit, help="Post samples target")
    parser.add_argument('--trg', default='0,0,0', help="Trigger trinary (1,0,0 or 1,0,1 or 1,1,1)")
    parser.add_argument('--event0', default='0,0,0', help="Event0 trinary (1,0,0 or 1,0,1)")
    parser.add_argument('--event1', default='0,0,0', help="Event1 trinary (1,0,0 or 1,0,1)")
    parser.add_argument('--rgm', default='0,0,0', help="RGM trinary")
    parser.add_argument('--translen', default=0, type=int, help="Translen size")
    parser.add_argument('--spad', default=None, help="SPAD trinary")
    parser.add_argument('--auto_soft', default=1, type=int, help="Enable auto soft trigger")
    parser.add_argument('--demux', default=0, type=int, help="Enable on uut demuxing")

    parser.add_argument('uutnames', nargs='+', help="uut hostnames")
    return parser

if __name__ == '__main__':
    run_main(get_parser().parse_args())

