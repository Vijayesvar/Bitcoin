import sys

from script import script
from backend.util.util import little_endian, encode_varint, decode_base58, little_endian_to_int, hash256, bytes_needed


ZERO_HASH = b"\0" * 32
REWARD = 50

PRIVATE_KEY = (
    "59024195091230105596801455306913435815673319996141880726735464739248197324364"
)
MINER_ADDRESS = "1LYgXwYXw16GJXgDwHV7aCNijnQWYEdc1C"
SIGHASH_ALL = 1


def calculate_merkle_root(transactions):
    """
    Calculate the Merkle root from a list of transactions.
    """
    tx_ids = [tx.Tx_Id for tx in transactions]
    if not tx_ids:
        return ZERO_HASH.hex()

    while len(tx_ids) > 1:
        if len(tx_ids) % 2 == 1:  # Duplicate the last hash if odd number of transactions
            tx_ids.append(tx_ids[-1])
        new_level = []
        for i in range(0, len(tx_ids), 2):
            new_hash = hash256((bytes.fromhex(tx_ids[i]) + bytes.fromhex(tx_ids[i + 1]))).hex()
            new_level.append(new_hash)
        tx_ids = new_level
    return tx_ids[0]


class CoinbaseTx:
    def __init__(self, block_height):
        self.block_height_in_little_endian = little_endian(
            block_height, bytes_needed(block_height)
        )

    def coinbase_transaction(self):
        prev_tx = ZERO_HASH
        prev_index = 0xFFFFFFFF
        tx_ins = [TxIn(prev_tx, prev_index)]
        tx_ins[0].script_sig.cmds.append(self.block_height_in_little_endian)

        tx_outs = []
        target_amount = REWARD * 100000000
        target_h160 = decode_base58(MINER_ADDRESS)
        target_script = script.p2publickeyhashscript(target_h160)
        tx_outs.append(TxOut(amount=target_amount, script_pubkey=target_script))
        coinbase_tx = Tx(1, tx_ins, tx_outs, 0)
        coinbase_tx.Tx_Id = coinbase_tx.id()
        return coinbase_tx


class Tx:
    def __init__(self, version, tx_ins, tx_outs, locktime):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime

    def id(self):
        return self.hash().hex()

    def hash(self):
        return hash256(self.serialize())[::-1]

    def serialize(self):
        result = little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))

        for tx_in in self.tx_ins:
            result += tx_in.serialize()

        result += encode_varint(len(self.tx_outs))

        for tx_out in self.tx_outs:
            result += tx_out.serialize()

        result += little_endian(self.locktime, 4)

        return result
    
    def sig_hash(self, input_index, script_pubkey):
        s = little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))

        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                s += TxIn(tx_in.prev_tx, tx_in.prev_index, script_pubkey).serialize()
            else:
                s += TxIn(tx_in.prev_tx, tx_in.prev_index).serialize()

        s += encode_varint(len(self.tx_outs))

        for tx_out in self.tx_outs:
            s += tx_out.serialize()

        s += little_endian(self.locktime, 4)
        s += little_endian(SIGHASH_ALL, 4)
        h256 = hash256(s)
        return int.from_bytes(h256, "big")

    
    def sign_input(self, input_index, private_key, script_pubkey):
        z=self.sig_hash(input_index, script_pubkey)
        der = private_key.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, "big")
        sec = private_key.point.sec()
        self.tx_ins[input_index].script_sig = script([sig, sec])

    def verify_input(self, input_index, script_pubkey):
        tx_in = self.tx_ins[input_index]
        z = self.sig_hash(input_index, script_pubkey)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)

    def is_coinbase(self):
        """
        Check if the transaction is a coinbase transaction.
        """
        if len(self.tx_ins) != 1:
            return False

        first_input = self.tx_ins[0]
        if first_input.prev_tx != ZERO_HASH:
            return False
        if first_input.prev_index != 0xFFFFFFFF:
            return False
        return True

    def to_dict(self):
        """
        Convert the transaction to a JSON-serializable dictionary.
        """
        tx_ins_serialized = [
            {
                "prev_tx": tx_in.prev_tx.hex(),
                "prev_index": tx_in.prev_index,
                "script_sig": tx_in.script_sig.to_dict(),
                "sequence": tx_in.sequence
            }
            for tx_in in self.tx_ins
        ]

        tx_outs_serialized = [
            {
                "amount": tx_out.amount,
                "script_pubkey": tx_out.script_pubkey.to_dict()
            }
            for tx_out in self.tx_outs
        ]

        return {
            "version": self.version,
            "tx_ins": tx_ins_serialized,
            "tx_outs": tx_outs_serialized,
            "locktime": self.locktime
        }


class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xFFFFFFFF):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        self.script_sig = script_sig if script_sig is not None else script()
        self.sequence = sequence

    def to_dict(self):
        """
        Convert TxIn to a JSON-serializable dictionary.
        """
        return {
            "prev_tx": self.prev_tx.hex(),
            "prev_index": self.prev_index,
            "script_sig": self.script_sig.to_dict(),
            "sequence": self.sequence
        }

    def serialize(self):
        result = self.prev_tx[::-1]
        result += little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += little_endian(self.sequence, 4)
        return result


class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def to_dict(self):
        """
        Convert TxOut to a JSON-serializable dictionary.
        """
        return {
            "amount": self.amount,
            "script_pubkey": self.script_pubkey.to_dict()
        }

    def serialize(self):
        result = little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result

