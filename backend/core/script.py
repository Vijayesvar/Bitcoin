import sys
sys.path.append('/home/vijay/Desktop/Bitcoin/backend')  # Add backend to sys.path
from util.util import little_endian, encode_varint

class script:
    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds


    def serialize(self):
        # initialize what we'll send back
        result = b""
        # go through each cmd
        for cmd in self.cmds:
            # if the cmd is an integer, it's an opcode
            if type(cmd) == int:
                # turn the cmd into a single byte integer using int_to_little_endian
                # result += int_to_little_endian(cmd, 1)
                result += little_endian(cmd, 1)
            else:
                # otherwise, this is an element
                # get the length in bytes
                length = len(cmd)
                # for large lengths, we have to use a pushdata opcode
                if length < 75:
                    # turn the length into a single byte integer
                    result += little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    # 76 is pushdata1
                    result += little_endian(76, 1)
                    result += little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    # 77 is pushdata2
                    result += little_endian(77, 1)
                    result += little_endian(length, 2)
                else:
                    raise ValueError("too long an cmd")

                result += cmd
        # get the length of the whole thing
        total = len(result)
        # encode_varint the total length of the result and prepend
        return encode_varint(total) + result
            
    @classmethod
    def p2publickeyhashscript(cls, hash160):
        # Pass the arguments as a list
        return cls([0x76, 0xa9, hash160, 0x88, 0xac])

    def to_dict(self):
        """
        Convert the script to a JSON-serializable dictionary.
        """
        return {"cmds": [cmd.hex() if isinstance(cmd, bytes) else cmd for cmd in self.cmds]}
