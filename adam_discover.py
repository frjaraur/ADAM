#!/usr/bin/python3
import sys, getopt, ipaddress,os,re

import threading
from queue import Queue

import numpy

import time
import subprocess



num_threads = 4

array_discoveredHosts=[]

lock = threading.Lock()

class IPobj:
    def __init__(self, ip):
        print ("OBJECT IP:"+ip )

    def addLabel(self,label,value):
        print ("LABEL: ["+label+"]")
        print ("VALUE: ["+value+"]")


def ICMPSimplePing(ip):
    while True:
        ret = subprocess.call("ping -c 3 %s" % ip,
                shell=True,
                stdout=open('/dev/null', 'w'),
                stderr=subprocess.STDOUT)
        if ret == 0:
            print ("%s: is alive" % ip)
            return True
        else:
            ADAMDebug(debug,"%s: did not respond" % ip)
            return False


def ADAMDebug(debug,debug_text):
    if debug:
        print ("[DEBUG] >>" + debug_text)

def ADAMDiscover(ip):
    #for ip in ipaddresses: 
        ADAMDebug(debug,"Discover IP " + ip)
        if ICMPSimplePing(ip):
            ADAMDebug(debug,"Creamos objeto...")
            obj=IPobj(ip)
            obj.addLabel("IPADDRESS",ip)
            global array_discoveredHosts
            array_discoveredHosts.append(obj)    
    

def do_ADAMProcess(ipaddresses):
     # pretend to do some lengthy work.
    for ip in ipaddresses:
        ADAMDebug(debug,"["+threading.current_thread().name+"] IP --> "+ip) 
        ADAMDiscover(ip)
    
    # Make sure the whole print completes or threads can mix up output in one line.
    with lock:

        print (threading.current_thread().name,'[%s]' % ', '.join(map(str, ipaddresses))) 

# The worker thread pulls an item from the queue and processes it
def ADAMProcess(q,ipadresses):
    while True:
        ipaddresses = q.get()
        do_ADAMProcess(ipaddresses)
        q.task_done()


def GetIpRange(range):
    print ("Range "+ range)
    try:
        #range_ip_addresses = ipaddress.ip_network(range).hosts()
        array_ipaddresses = list()
        for IP in ipaddress.ip_network(range).hosts():
            #ADAMDebug("-->"+str(IP))
            array_ipaddresses.append(str(IP))
        return array_ipaddresses

    except ValueError:
        print ("Not a valid IP /Network Class Range...Try again...")   
        exit()

def ShowHelp(vmyname):
   print ("HELP ("+vmyname+")")
   sys.exit(2)


def main(argv):
    global debug,inputfile,outputfile
    inputfile = ''
    outputfile = ''
    debug=False
    myname=os.path.basename(__file__)
    myips=list()
    try:
      opts, args = getopt.getopt(argv,"Dhi:o:R:",["ifile=","ofile=","Range=","Debug"])
    except getopt.GetoptError:
      ShowHelp(myname)

    for opt, arg in opts:
      if opt == '-h':
   #          /* print 'test.py -i <inputfile> -o <outputfile>' */
        ShowHelp(myname)
      elif opt in ("-D", "--Debug"):
        debug=True
        print ("DEBUG MODE")
      elif opt in ("-i", "--ifile"):
        inputfile = arg
      elif opt in ("-o", "--ofile"):
        outputfile = arg
      elif opt in ("-R", "--Range"):
        iprange = arg       
        myips=GetIpRange(iprange)
        total_ipaddresses_in_range=len(myips)
        #print ("ARRAY LEN: "+str(len(myips)))
        start = time.perf_counter()
        if total_ipaddresses_in_range > num_threads :
            myipchunks=numpy.array_split(myips, num_threads)
            #chunk_array(10, myips)
            q = Queue()
            for ipchunk in myipchunks: 
                t = threading.Thread(target=ADAMProcess,args=(q,ipchunk))
                t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
                t.start()
            
            for ipchunk in myipchunks:             
                q.put(ipchunk)
                    
            q.join() 
           # for ip in ipchunk: 
           #     print ("IP --> "+str(ip))
        else:
            #Discover one IP
            for ip in myips: 
                ADAMDiscover(ip)
                
        total_ipaddresses_discovered=len(array_discoveredHosts)
        print ("Discovered "+str(total_ipaddresses_discovered)+" from "+str(total_ipaddresses_in_range)+" possible IPs")       
        print('time: '+str(round((time.perf_counter() - start),2))+"s")


if __name__ == "__main__":
    main(sys.argv[1:])

