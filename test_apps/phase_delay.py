#!/usr/bin/env python3

import os
import argparse
import numpy as np
from scipy.signal import hilbert, chirp
from prettytable import PrettyTable

#./phase_delay_multi.py --s_clk=20000 --fsig=20 --method=1,2,4 --type=32 BROTH/*

def run_test(args):
    if len(args.files) < 2:
        exit("More than 2 files required")
    methods = args.method.split(",")
    for method in methods:
        run_comparison(args,method)

def run_comparison(args,method):
    files = args.files.copy()
    t = PrettyTable(['File1','File2','Diff(Nanoseconds)','Diff as % of sample clock'])
    def file_comparator(first,array):
        for second in array:
            phase_diff, degrees, sec, percent = calc_delay(first,second,method,args)
            first_filename = os.path.basename(first)
            second_filename = os.path.basename(second)
            t.add_row([first_filename, second_filename, sec, percent])
        t.add_row(["-","-","-","-"]) # Empty row to demarcate first box in comparison
        if len(array) > 1:
            file_comparator(array.pop(0),array)
            return
    file_comparator(files.pop(0),files)
    print("| Method {} | fsig: {} s_clk: {}".format(method,args.fsig,args.s_clk))
    print(t)

def calc_delay(file1,file2,method,args):
    method = int(method)
    x1 = np.fromfile(file1, dtype=args.type)
    x2 = np.fromfile(file2, dtype=args.type)
    # Remove offsets
    x1 = x1 - np.mean(x1)
    x2 = x2 - np.mean(x2)
    # Scale x2 to match x1
    m1 = np.mean(abs(x1))
    x2 = x2 * (m1/np.mean(abs(x2)))
    # Difference
    y3 = (x2 - x1) / m1
    if method == 1:
        # Using 'Taylor Series' method
        phase_diff = np.mean(abs(np.subtract(x2, x1)) / m1)
        #phase_diff = np.mean(np.subtract(x2, x1) / m1)

    elif method == 2:
        # Using phase sensitive detector
        phase_diff = np.arccos(
            np.dot(x1, x2) / (np.linalg.norm(x1)*np.linalg.norm(x2)))

    elif method == 3:
        exit("bad method 3")
        # FFT method
        fft_x1 = np.fft.fft(x1)
        fft_x2 = np.fft.fft(x2)
        #print "ffts = ", fft_x1, fft_x2
        l1 = len(fft_x1)
        l2 = len(fft_x2)
        phase_diff = np.angle(fft_x1[0:l1+1/2] / fft_x2[0:l2+1/2])
        phase_diff = float(np.pi) - float(phase_diff[0])

    elif method == 4:
        # Hilbert transform method
        x1h = hilbert(x1)
        x2h = hilbert(x2)
        ph_diff = np.angle(x1h/x2h)
        phase_diff = abs(ph_diff[0])

    degrees = phase_diff * (1/(np.pi / 180))
    sec = degrees / (360 * args.fsig)
    percent = sec * 100 * args.s_clk
    #sec = phase_diff / (np.pi * args.fsig);
    #sec = phase_diff / (360 * args.fsig);
    return  round(phase_diff,2), round(degrees,2), round(sec * 1000000000,2), round(percent,2)
    #return  round(phase_diff,2), round(degrees,2), "{:0.2e}".format(sec), round(percent,2)


def run_main():
    parser = argparse.ArgumentParser(description='awg speed test')
    parser.add_argument('--fsig', type=int, default=488,help='Frequency of the signal.',required=True)
    parser.add_argument('--s_clk', type=int, default=48800,help='Frequency of the clk.',required=True)

    parser.add_argument('--method',default="1",type=str,help='Which methods to use. ie 1,2,4')
    parser.add_argument('--type', type=int, default=16,help='16 or 32 bit data')
    parser.add_argument('files',help='Files to process',nargs='+')

    args = parser.parse_args()
    args.type = np.int16 if args.type == 16 else np.int32
    run_test(args)


if __name__ == '__main__':
    run_main()
