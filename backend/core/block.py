class Block:
    def __init__(self, height, blocksize, blockheader, txcount, txs):
        self.height =height
        self.blockheader=blockheader
        self.blocksize=blocksize
        self.txcount=txcount
        self.txs=txs


