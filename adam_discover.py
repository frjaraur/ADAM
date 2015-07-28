#!/usr/bin/python3
import sys, getopt, ipaddress,os,re

import threading
from queue import Queue

import numpy

import time


num_threads = 4

lock = threading.Lock()

class ADAMobject(object):
    def __init__(self, ip):
        print ("OBJECT IP:"+ip )

# def Discover(numthread,ipaddresses):
#     print ("THREAD: " + str(numthread))
#     with lock:
#         print ("IPADRESSES:")
#         print ('[%s]' % ', '.join(map(str, ipaddresses))) 
#     item = q.get()
#     print(threading.current_thread().name,item)
#     q.task_done()

def do_Discover(ipaddresses):
    #time.sleep(.1) # pretend to do some lengthy work.
    for ip in ipaddresses: 
        print ("["+threading.current_thread().name+"] IP --> "+str(ip))
    
    # Make sure the whole print completes or threads can mix up output in one line.
    with lock:
        #print(threading.current_thread().name,item)
        print ("IPADRESSES:")
        print (threading.current_thread().name,'[%s]' % ', '.join(map(str, ipaddresses))) 

# The worker thread pulls an item from the queue and processes it
def Discover(q,ipadresses):
    while True:
        ipaddresses = q.get()
        do_Discover(ipaddresses)
        q.task_done()


def GetIpRange(range):
    print ("Range "+ range)
    net = ipaddress.ip_network(range)
    array_ipaddresses = list()

    for IP in net:
        #print (IP)
        array_ipaddresses.append(IP)

    return array_ipaddresses

def ShowHelp(vmyname):
   print ("HELP ("+vmyname+")")
   sys.exit(2)


def main(argv):
    inputfile = ''
    outputfile = ''
    myname=os.path.basename(__file__)
    myips=list()
    try:
      opts, args = getopt.getopt(argv,"hi:o:R:",["ifile=","ofile=","Range="])
    except getopt.GetoptError:
      ShowHelp(myname)

    for opt, arg in opts:
      if opt == '-h':
   #          /* print 'test.py -i <inputfile> -o <outputfile>' */
        ShowHelp(myname)

      elif opt in ("-i", "--ifile"):
        inputfile = arg
      elif opt in ("-o", "--ofile"):
        outputfile = arg
      elif opt in ("-R", "--Range"):
        iprange = arg
        myips=GetIpRange(iprange)
        myipchunks=numpy.array_split(myips, num_threads)
        
        
        
        #chunk_array(10, myips)
        q = Queue()
      
        for ipchunk in myipchunks: 
            #print ('[%s]' % ', '.join(map(str, ipchunk)))
            #Discover(ipchunk)
            
            t = threading.Thread(target=Discover,args=(q,ipchunk))
            t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
            t.start()
            
        
        start = time.perf_counter()
        for ipchunk in myipchunks:             
            q.put(ipchunk)
                
        q.join() 
           # for ip in ipchunk: 
           #     print ("IP --> "+str(ip))

        print('time:',time.perf_counter() - start)


if __name__ == "__main__":
    main(sys.argv[1:])

