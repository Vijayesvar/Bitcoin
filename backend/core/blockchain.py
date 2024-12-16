import sys
sys.path.append('/home/vijay/Desktop/bitcoin/')

from block import Block
from blockheader import Blockheader
from blockheader import hash256
from database.database import BlockchainDB
from transaction import CoinbaseTx
import time

zero_hash = '0' * 64  # Genesis block's previous hash
version = 1

class Blockchain:
    def __init__(self):
        pass

    def writeondisk(self, block):
        blockchaindb = BlockchainDB()
        blockchaindb.write(block)

    def getlastblock(self):
        blockchaindb = BlockchainDB()
        return blockchaindb.lastBlock()

    def initialize_blockchain(self):
        # Check if a genesis block exists; if not, create it
        last_block = self.getlastblock()
        if last_block is None:
            print("No genesis block found. Creating genesis block.")
            self.genesis_block()

    def genesis_block(self):
        blockheight = 0
        prevblockhash = zero_hash
        self.addblock(blockheight, prevblockhash)

    def addblock(self, blockheight, prevblockhash):
        timestamp = int(time.time())
        transaction_instance = CoinbaseTx(blockheight)
        transaction = transaction_instance.coinbase_transaction()
        merkleroot = transaction.id()
        bits = 'ffff001f'
        blockheader = Blockheader(version, prevblockhash, merkleroot, timestamp, bits)
        blockheader.mine()
        print(f"Block {blockheight} mined successfully with nounce value of {blockheader.nonce}")
        block_data = [
            Block(
                blockheight,
                1,
                blockheader.__dict__,
                1,
                transaction.to_dict()  # Use to_dict here
            ).__dict__
        ]
        self.writeondisk(block_data)

    def main(self):
        lastblock = self.getlastblock()
        if(lastblock is None):
            self.genesis_block()  
        while True:
            prevblock = self.getlastblock()
            if prevblock is None:
                print("Blockchain is empty. Creating genesis block.")
                self.genesis_block()
                continue
            blockheight = prevblock["height"] + 1
            prevblockhash = prevblock["blockheader"]["blockhash"]
            self.addblock(blockheight, prevblockhash)

if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.main()
 