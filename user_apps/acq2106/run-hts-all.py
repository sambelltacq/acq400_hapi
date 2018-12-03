#!/usr/bin/python

import argparse
import subprocess
import os
import sys
import time
import glob
import shutil
import acq400_hapi

class Struct(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def map_uuts():
    ids = subprocess.check_output(["get-ident-all"]).split('\n')
    uut_port_map = {}
    maps = [ id.split(' ') for id in ids ]
    for map in maps:
        if len(map) == 4 and map[2].startswith('acq2106'):
            s = Struct(uut=map[2], lport=map[1], rport=map[3])
            uut_port_map[s.uut] = s

    return uut_port_map

uut_port_map = map_uuts()
uuts = []


def make_fifos(args):
    args.fifos = []
    for uut in args.uuts:
        fn = "/tmp/{}.hts".format(uut)
        try:
            os.mkfifo(fn)            
        except OSError, e:
            if e.errno != 17:            
                sys.exit("ERROR OSError, {}", e)
                
        args.fifos.append(fn)
            
scmd = ('python', '-u', './user_apps/acq400/sync_role.py')

def set_sync_roles(args):
    print("set_sync_roles")
    # --toprole=master,fptrg --fclk=10M --enable_trigger=1 $UUTS
    cmd = []
    cmd.extend(scmd)
    toprole = 'master'
    if args.etrg == 1:
        toprole += ',fptrg'
    cmd.append('--toprole={}'.format(toprole))
    cmd.append('--fclk={}'.format(args.fclk))
    for uut in args.uuts:
        cmd.append(uut)
    print(cmd)
    subprocess.check_call(cmd)        

time0 = 0

def wait_for_state(args, state, timeout=0):
    global time0
    if time0 == 0:
        time0 = time.time()  
    for uut in uuts:
        olds = ""
        finished = False
        dots = 0
        pollcat = 0
        
        while not finished:
            st = uut.s0.CONTINUOUS_STATE.split(' ')[1]
            finished = st == state
            news = "polling {}:{} {} waiting for {}".format(uut.uut, st, 'DONE' if finished else '', state)
            if news != olds: 
                sys.stdout.write("\n{:06.2f}: {}".format(time.time() - time0, news))
                olds = news
            else:
                sys.stdout.write('.')
                dots += 1
                if dots >= 20:                    
                    dots = 0
                    olds = ""
            if not finished:
                if timeout and (time.time() - time0) > timeout:
                    sys.exit("\ntimeout waiting for {}".format(news))
                time.sleep(1)
            pollcat += 1
    print("")
            
def release_the_trigger(args):
    
    print("RELEASE the trigger REMOVEME when hardware fixed")
    cmd = []
    cmd.extend(scmd)
    cmd.append('--enable_trigger=1')
    cmd.append(args.uuts[0])
    print(cmd)
    subprocess.check_call(cmd)     

def init_shot(args):
    global uuts
    make_fifos(args)
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]
    set_sync_roles(args)
    
def _store_shot(shot):
    print("store_shot {}".format(shot))    
    src = os.getenv('HTSDATA')
    srcports = glob.glob('{}/*'.format(src))
    base = os.getenv('HTSARCHIVE', os.path.dirname(src))
    shotbase = "{}/SHOTS/{:08d}".format(base, shot)
    print("copy from {} to {}".format(src, shotbase))
    
    try:
        os.makedirs(shotbase)
#OSError: [Errno 17] File exists: '/mnt/datastream/SHOTS/00000144'
    except OSError, e:
        if e.errno == 17:
            sys.exit("WARNING: {}\nrefusing to overwrite duplicate shot, please backup by hand".format(e))
        else:
            sys.exit("ERROR OSError, {}", e) 
        
    
    for sp in srcports:
        cmd = [ 'sudo', 'mv', sp, shotbase]
        subprocess.check_call(cmd)   
    
    cmd = [ 'du', '-sh', shotbase]
    subprocess.check_call(cmd)
    
def store_shot(args):
    wait_for_state(args, 'IDLE')
    shot = [ u.s1.shot for u in uuts]
    
    s0 = shot[0]
    for ii, s1 in enumerate(shot[1:]):
        if s0 != s1:
            print("WARNING: uut {} shot {} does not equal master {}".format(uuts[ii].uut, s1, s0))
            
    _store_shot(int(shot[0]))
    
    
    
# sudo mv /mnt/datastream/ACQ400DATA/* /mnt/datastream/SHOT_0134/    
def run_shot(args):
    cmd = ['mate-terminal']
    tabdef = '--window-with-profile=Default'

    for ii, uut in enumerate(args.uuts):
        ports = uut_port_map[uut]
        cmd.append(tabdef)
        cmd.append('--title={}'.format(uut))
        cmd.append('--command=run-hts {} {} {} {}'.\
                format(uut, ports.lport, args.secs, ports.rport))
        tabdef = '--tab-with-profile=Default'
        
        cmd.append(tabdef)
        cmd.append('--title={}.hts'.format(uut))
        cmd.append('--command=cat {}'.format(args.fifos[ii]))                

    print(cmd)
    subprocess.check_call(cmd)

    wait_for_state(args, 'ARM', timeout=45)
    
    if args.etrg == 1:
       release_the_trigger(args) 
       
    if args.store == 1:
        store_shot(args)
        
       

def run_main():
    parser = argparse.ArgumentParser(description='run hts all uuts')
    parser.add_argument('--secs', default=100, help='seconds to run')
    parser.add_argument('--etrg', type=int, default=0, help='1: enable external trg')
    parser.add_argument('--fclk', type=str, default='10M', help='sample clock before decimation')
    parser.add_argument('--store', type=int, default=0, help='1: store shot after capture')
    parser.add_argument('uuts', nargs='+', help='uut')
    args = parser.parse_args()
    init_shot(args)
    run_shot(args)

# execution starts here

if __name__ == '__main__':
    run_main()
