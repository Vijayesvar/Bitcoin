import hashlib

def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

class Blockheader:
    def __init__(self, version, prevblockhash, merkletree, timestamp, bits):
        self.version=version
        self.prevblockhash=prevblockhash
        self.merkletree=merkletree
        self.timestamp=timestamp
        self.bits=bits
        self.blockhash= ''
        self.nonce=0

    def mine(self):
        while(self.blockhash[0:4]) != '0000':
            # print(type(self.version))
            # print(type(self.prevblockhash))
            self.blockhash=hash256((str(self.version) + str(self.prevblockhash) + str(self.merkletree) + str(self.timestamp) + str(self.bits) + str(self.nonce)).encode()).hex()
            self.nonce +=1
            print(f"mining strated {self.nonce}", end='\r')