import hashlib
import sys
from Crypto.Hash import RIPEMD160
from hashlib import sha256
from math import log
sys.path.append('/home/vijay/Desktop/bitcoin/blockchain/backend')
from core.EllepticCurve.EllepticCurve import BASE58_ALPHABET



def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def hash160(s):
    return RIPEMD160.new(sha256(s).digest()).digest()

def bytes_needed(n):
    if n == 0:
        return 1
    return int(log(n,256))+1

def little_endian(n, length):
    return n.to_bytes(length, 'little') 

def little_endian_to_int(b):
    return int.from_bytes(b, 'little')



def decode_base58(s):
    num = 0

    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)

    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]
    
    
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError(f'bad address {checksum} {hash256(combined[:-4][:4])}')
    
    return combined[1:-4]


    
def encode_varint(i):
    """encodes an integer as a varint"""
    if i < 0xFD:
        return bytes([i])
    elif i < 0x10000:
        return b"\xfd" + little_endian(i, 2)
    elif i < 0x100000000:
        return b"\xfe" + little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b"\xff" + little_endian(i, 8)
    else:
        raise ValueError("integer too large: {}".format(i))
    