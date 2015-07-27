#!/usr/bin/python3
import sys, getopt, ipaddress,os,re

from subprocess import Popen, PIPE
from threading import Thread

from multiprocessing import Process, Queue

import numpy

num_threads = 4


class Pinger(object):
    def __init__(self, hosts):
        for host in hosts:
            #q.put ([42,None,"pinging "+ str(host)])
            pa = PingAgent(host)
            pa.start()


class PingAgent(Thread):
    def __init__(self, host):
        Thread.__init__(self)
        self.host = host

    def run(self):
        p = Popen('ping -n 1 ' + self.host, stdout=PIPE)
        m = re.search('Average = (.*)ms', p.stdout.read())
        if m: print ('Round Trip Time: %s ms -' % m.group(1), self.host)
        else: print ('Error: Invalid Response -', self.host)


# def pinger(q,ips):
#     for ping_ip in ips:
#         while True:
#             q.put ([42,None,"pinging "+ str(ping_ip)])


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
        for ipchunk in myipchunks: 
            print ('[%s]' % ', '.join(map(str, ipchunk)))         
   # q=Queue()
    #for i in range(num_threads):
#     for i in myips:
#         p = Process(target=Pinger,args=(i ))
#         p.start()
#         print (q.get())
#         p.join()



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

if __name__ == "__main__":
    main(sys.argv[1:])

