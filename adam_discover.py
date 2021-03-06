#!/usr/bin/python3
import sys, getopt, ipaddress, os, re, socket

import threading
from queue import Queue

import numpy

import time
import subprocess

#from collections import defaultdict

import adam_ssh

num_threads = 4

array_discoveredHosts = []
# dict_discoveredData={}
# dict_discoveredData=defaultdict(dict)
dict_discoveredData = dict()
lock = threading.Lock()

standard_tcp_ports = [21, 22, 23, 80, 135, 137, 138, 139, 8080, 443]
standard_ssh_ports = [22]


class IPobj:
    def __init__(self, ip):
        print ("OBJECT IP:" + ip)
        dict_discoveredData[ip] = dict()

    def addLabel(self, ip, label, value):
        print ("LABEL: [" + label + "]")
        print ("VALUE: [" + value + "]")
        dict_discoveredData[ip][label] = value
    
    def CheckIfLabel(self,ip,label):
        print ("Check If LABEL "+label+" para la IP "+ip)
        try:
            #dict_discoveredData.get(ip, dict_discoveredData.get('firstName', myDict.get('userName')))
            if dict_discoveredData[ip][label]:
                #print ("---------------->LABEL "+label+" exists for IP "+ip)
                return True
        except:
            #print ("No value for label %s on IP %s" % (label,ip))
            ADAMDebug(debug,"No value for label %s on IP %s" % (label,ip))
            return False 

    def getLabel(self,ip,label):
        print ("Check If LABEL "+label+" para la IP "+ip)
        try:
            #dict_discoveredData.get(ip, dict_discoveredData.get('firstName', myDict.get('userName')))
            print (dict_discoveredData[ip][label])
            print ("---------------->LABEL "+label+" exists for IP "+ip)
            return True
        except:
            print ("No value for label %s on IP %s" % (label,ip))
            ADAMDebug(debug,"No value for label %s on IP %s" % (label,ip))
            return False 

def CheckTCPPort(ip, port):
    s = socket.socket()
    # s.setblocking(0)
    s.settimeout(10)
    print ("Attempting to connect to %s on port %s" % (ip, port))
    try:
        s.connect((ip, port))
        print ("Connected to %s on port %s" % (ip, port))
        return True
    except socket.error:
        print ("Connection to %s on port %s failed" % (ip, port))
        return False

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
            ADAMDebug(debug, "%s: did not respond" % ip)
            return False


def ADAMDebug(debug, debug_text):
    if debug:
        print ("[DEBUG] >>" + debug_text)

def ADAMDiscover(ip):
    # for ip in ipaddresses: 
    ADAMDebug(debug, "Discover IP " + ip)
    if not ICMPSimplePing(ip):
        return 0
        
    ADAMDebug(debug, "Creamos objeto...")
    obj = IPobj(ip)
    obj.addLabel(ip, "IPADDRESS", ip)
    global array_discoveredHosts
    array_discoveredHosts.append(obj)
    for port in standard_tcp_ports:
        if CheckTCPPort(ip, port):
            obj.addLabel(ip, "PORT_TCP_" + str(port), "alive")
            if port in standard_ssh_ports:
                obj.addLabel(ip, "SSH_ENABLED", "true")
    
    #SSH       
    if obj.CheckIfLabel(ip, "SSH_ENABLED"):            
        adam_ssh.SSH_test(ip)






def do_ADAMProcess(ipaddresses):
     # pretend to do some lengthy work.
    for ip in ipaddresses:
        ADAMDebug(debug, "[" + threading.current_thread().name + "] IP --> " + ip) 
        ADAMDiscover(ip)
    
    # Make sure the whole print completes or threads can mix up output in one line.
    with lock:

        print (threading.current_thread().name, '[%s]' % ', '.join(map(str, ipaddresses))) 

# The worker thread pulls an item from the queue and processes it
def ADAMProcess(q, ipadresses):
    while True:
        ipaddresses = q.get()
        do_ADAMProcess(ipaddresses)
        q.task_done()


def GetIpRange(range):
    print ("Range " + range)
    try:
        # range_ip_addresses = ipaddress.ip_network(range).hosts()
        array_ipaddresses = list()
        for IP in ipaddress.ip_network(range).hosts():
            # ADAMDebug("-->"+str(IP))
            array_ipaddresses.append(str(IP))
        return array_ipaddresses

    except ValueError:
        print ("Not a valid IP /Network Class Range...Try again...")   
        exit()

def ShowHelp(vmyname):
   print ("HELP (" + vmyname + ")")
   print ("\tOptions Available:\n\t-i [--ifile] Input file\n\t-o [--ofile] Output file\n\t-R [--Range] Range Of IPs\n")   
   sys.exit(2)


def main(argv):
    global debug, inputfile, outputfile
    inputfile = ''
    outputfile = ''
    debug = False
    myname = os.path.basename(__file__)
    myips = list()
    try:
      opts, args = getopt.getopt(argv, "Dhi:o:R:", ["ifile=", "ofile=", "Range=", "Debug"])
    except getopt.GetoptError:
      ShowHelp(myname)

    for opt, arg in opts:
      if opt == '-h':
   #          /* print 'test.py -i <inputfile> -o <outputfile>' */
        ShowHelp(myname)
      elif opt in ("-D", "--Debug"):
        debug = True
        print ("DEBUG MODE")
      elif opt in ("-i", "--ifile"):
        inputfile = arg
      elif opt in ("-o", "--ofile"):
        outputfile = arg
      elif opt in ("-R", "--Range"):
        iprange = arg       
        myips = GetIpRange(iprange)
        total_ipaddresses_in_range = len(myips)
        # print ("ARRAY LEN: "+str(len(myips)))
        start = time.perf_counter()
        if total_ipaddresses_in_range > num_threads :
            myipchunks = numpy.array_split(myips, num_threads)
            # chunk_array(10, myips)
            q = Queue()
            for ipchunk in myipchunks: 
                t = threading.Thread(target=ADAMProcess, args=(q, ipchunk))
                t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
                t.start()
            
            for ipchunk in myipchunks:             
                q.put(ipchunk)
                    
            q.join() 
           # for ip in ipchunk: 
           #     print ("IP --> "+str(ip))
        else:
            # Discover one IP
            for ip in myips: 
                ADAMDiscover(ip)
                
        total_ipaddresses_discovered = len(array_discoveredHosts)
        print ("Discovered " + str(total_ipaddresses_discovered) + " from " + str(total_ipaddresses_in_range) + " possible IPs")       
        print('time: ' + str(round((time.perf_counter() - start), 2)) + "s")

    # print (dict_discoveredData.items())
    # for dict_discoveredDataIP,dict_discoveredDatalabel,dict_discoveredDatavalue in dict_discoveredData.items():
        # print (dict_discoveredDataIP)
    #dict_discoveredData_Sorted=sorted(dict_discoveredData)
    for discovered_ip in dict_discoveredData.keys():
        print ("->" + discovered_ip)
        for discovered_label in dict_discoveredData[discovered_ip].keys():    
            print (discovered_label + "--->" + dict_discoveredData[discovered_ip][discovered_label])


if __name__ == "__main__":
    main(sys.argv[1:])

