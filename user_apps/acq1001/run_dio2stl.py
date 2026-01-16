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

import argparse
import time
import sys

import acq400_hapi
from acq400_hapi.acq400 import AcqPorts, netclient


def print_stderr(text):
    sys.stderr.write(f"{text}\n")
    sys.stderr.flush()


def run_shot(args):
    print_stderr(args)
    print_stderr("running a shot")
    start_time = time.time()
    end_time = start_time + args.runtime
    bytes_required = args.MB * 1024 * 1024
    bytestogo = bytes_required
    total_received = 0
    acq400_hapi.cleanup.init()

    with netclient.Netclient(args.uuts[0], AcqPorts.DIO2STL) as nc:
        print_stderr("Connection established. Streaming data...")
        while True:
            if args.runtime > 0 and time.time() > end_time:
                break
            if args.MB > 0 and bytestogo <= 0:
                break
            rx = nc.sock.recv(4096)
            if not rx:
                break
            sys.stdout.buffer.write(rx)
            rx_len = len(rx)
            total_received += rx_len
            bytestogo -= rx_len

        sys.stdout.buffer.flush()
    print_stderr(f"Shot ended. Total bytes captured {total_received}")


def run_main():
    parser = argparse.ArgumentParser(description="dio2stl demo")
    parser.add_argument("uuts", nargs=1, help="uut ")
    parser.add_argument("--MB", type=int, default=0, help="capture length in megabytes")
    parser.add_argument(
        "--runtime", default=0, type=int, help="How long to stream data for in seconds"
    )
    run_shot(parser.parse_args())


if __name__ == "__main__":
    run_main()
