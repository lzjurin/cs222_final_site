import numpy as np
from PIL import Image
from reedsolomon.reedsolo import RSCodec, ReedSolomonError
import symTable

class InvalidDataStreamException(Exception):
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return repr(err)

class InvalidImageStreamException(InvalidDataStreamException):
    def __init__(self, err):
        super(InvalidDataStreamException, self).__init__()

class Encoder(object):
    def __init__(self, k = 2, kind = "uniform_equitable", R=10):
        self.table = symTable.binarySymbolTable(2 ** k, kind)
        self.k = k # how many bits are grouped together

        # Reed Solomon Codes Generator
        self.rs = RSCodec(R)

    # Make sure you feed in a multiple of 8!
    def toBits(self, s, length=8):
        result = ""
        for c in s:
            bits = bin(ord(c))[2:].zfill(length)
            result += bits
        return result

    def toBytes(self, s):
        if len(s) % 8 != 0:
            s += '0' * (8 - (len(s) % 8))
        result = ""
        for b in range(len(s) / 8):
            byte = s[b*8:(b+1)*8]
            result += chr(int(str(byte), 2))
        return result

    # stream is string of 0/1
    def RSCEncode(self, stream):
        byte_stream = self.toBytes(stream)
        corrected_byte_stream = str(self.rs.encode(byte_stream))
        corrected_bit_stream = self.toBits(corrected_byte_stream)
        return corrected_bit_stream

    # stream is string of 0/1
    def RSCDecode(self, padded_stream):
        # convert to bytes
        padded_byte_stream = self.toBytes(padded_stream)
        try:
            byte_stream = str(self.rs.decode(padded_byte_stream)[0])
        except ReedSolomonError:
            raise ReedSolomonError

        bit_stream = self.toBits(byte_stream)
        return bit_stream

    # Get the tuples corresponding to each piece of data in the datastream
    def encode(self, stream):
        data = []
        for i in range(len(stream) / self.k):
            data.append(stream[i*self.k:(i+1)*self.k])
        size = len(data)
        if round(size ** 0.5) ** 2 != size:
            raise InvalidDataStreamException('Stream is not of square size')
        out = []
        for i in xrange(len(data)):
            try:
                out.append(self.table[int(data[i], 2)])
            except IndexError as e:
                print "Symbol table does not support encoding value {0} at index {1} in the stream".format(data[i], i)
                return None
        return out

    def decode(self, tuples):
        result = ""
        for symbol in tuples:
            decoded_symbol = symTable.decodeSymbol(symbol, self.table)
            bits = bin(decoded_symbol)[2:].zfill(self.k)
            result += bits
        return result

    # Convert encoded tuples into image data stream
    # Params: horizontal/vertical/square, repeat count
    def imageStreamRepeat(self, encoded, repeat=1, imageType='horizontal'):
        if imageType in ['horizontal', 'vertical']:
            tot = len(encoded) * repeat
            r = int(round(tot ** 0.5))
            if not r ** 2 == tot:
                raise InvalidImageStreamException('Resultant image will not be a square')
            if imageType == 'horizontal':
                return np.array(encoded).repeat(repeat, axis=0)
            else:
                return np.concatenate(np.stack(np.array_split(np.array(encoded).repeat(repeat, axis=0), r), axis=1))
        elif imageType == 'square':
            l = len(encoded) # length of stream
            s = int(round(l ** 0.5)) # side length of square
            if not s ** 2 == l:
                raise InvalidImageStreamException('Resultant image will not be a square')
            square = np.reshape(np.array([tup for tup in encoded]), (s,s,3))
            return np.concatenate(square.repeat(repeat, axis=0).repeat(repeat,axis=1))

    # Undo image stream
    def undoImageStream(self, stream, mult=1, imageType='square'):
        l = len(stream)
        d = int(round(l ** 0.5))

        if d ** 2 != l:
            raise InvalidImageStreamException("Stream is not of square size")

        if (imageType in ['horizontal', 'vertical'] and l % mult) or \
            (imageType == 'square' and l % (mult ** 2)):
            raise InvalidImageStreamException("Image stream to be undone has extra data (repeat {0})".format(mult))

        if imageType == 'horizontal':
            count = l / mult
            return map(tuple, [np.array(map(sum, zip(*stream[i * mult : (i + 1) * mult]))) / mult for i in xrange(count)])

        elif imageType == 'vertical':
            streaks = np.array_split(stream, d / mult)
            values = map(lambda streak: sum(np.array_split(streak, mult)) / mult, streaks)
            return map(tuple, np.concatenate(values))
        elif imageType == 'square':
            streaks = np.array_split(np.array(stream), d / mult)
            columnsums = map(lambda streak: sum(np.array_split(streak, mult)), streaks)
            values = map(lambda columnsum: np.array(map(lambda tups: sum(tups), np.array_split(columnsum, d / mult))) / (mult ** 2), columnsums)
            return map(tuple, np.concatenate(values))

class ImageConverter():
    def __init__(self):
        pass

    # Converts an image stream to an image in Pillow and saves it as a JPEG file, also returns the image object
    # Quality is an int on a scale from 1 (worst) to 95 (best)
    def streamToJPEG(self, encoding, quality=70, fileName = None):
        mode = 'RGB'
        size = encoding.size / 3

        size = int(len(encoding) ** 0.5)
        if (size ** 2) != len(encoding):
            raise InvalidImageStreamException('Resultant image will not be a square')
        image = Image.frombuffer(mode, (size, size), np.array(encoding, np.uint8).tostring(), 'raw', mode, 0, 1)
        if fileName:
            image.save(fileName, format='JPEG', quality=quality)
        return image

    # Converts a Pillow image object to an image stream
    def imageToStream(self, img):
        return list(img.getdata())

    # Converts a JPEG image located in a specific path to an image stream
    def JPEGtoStream(self, fileName):
        img = Image.open(fileName)
        return self.imageToStream(img)
