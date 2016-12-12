import random, util, symtable, sys, os
import numpy as np
from reedsolomon.reedsolo import ReedSolomonError

DATASIZE = (2 ** 16) / 8
REPEAT = 4
QUALITY = 100

args = sys.argv[1:]
filein = args[0]
savedir = 'out/' + ''.join(filein.split('.')[:-1])
if not os.path.exists(savedir):
    os.makedirs(savedir)

encoder = util.Encoder(k = 4, kind = "uniform_equitable")
converter = util.ImageConverter()

arr = [None] * DATASIZE
f = open(filein, "rb")
ind = 1

############
# Create image from data
def processData(num, arr):
    data = map(lambda x: [(x >> i) & 1 for i in reversed(xrange(8))] if x else [0] * 8, arr)
    data = ''.join(map(str, reduce(lambda x, y: x + y, data)))
    fileName=(savedir + '/{0:03d}.jpg'.format(num)) if type(num).__name__ == 'int' else (savedir + '/' + num)

    tuples = encoder.encode(data)
    squareimage = encoder.imageStreamRepeat(tuples, repeat=REPEAT, imageType='square')
    converter.streamToJPEG(squareimage, quality=QUALITY, fileName=fileName)
#############

try:
    byte = None
    while byte != "":
        byte = f.read(1)
        arr[(ind - 1) % DATASIZE] = ord(byte)
        ind += 1
        if not ind % 4096:
            processData(ind / 4096, arr)
    arr = [None] * DATASIZE
except:
    processData(ind / 4096, arr)
    f.close()

meta = [ord(c) for c in filein.split('/')[-1]]
byterep = []
while ind:
    byterep.append(ind % 256)
    ind /= 256
meta.extend(reversed(byterep))
meta.append(ord('\n'))
meta.extend([0] * (DATASIZE - len(meta)))
processData('metadata.jpg', meta)
