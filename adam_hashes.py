#!/usr/bin/python3
# Taken from stackoverflow example
import hashlib
#def hashfile(afile, hasher, blocksize=65536):
def hashfile(filename):
    f=open(filename, 'rb')
    hasher= hashlib.md5()
    blocksize=65536
    buf = f.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(blocksize)
    #return hasher.digest()
    return hasher.hexdigest()


fnamelst=["adam_discover.py","adam_discover.py.MAL","adam_snmp.py"]

#[(fname, hashfile(open(fname, 'rb'), hashlib.sha256())) for fname in fnamelst]
for fname in fnamelst:
	#print (hashfile(open(fname, 'rb'), hashlib.md5()))
	print (hashfile(fname))
