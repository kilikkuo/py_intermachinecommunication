import time
import socket
from op_code import OP_DATA_BEGIN, OP_DATA_END

class Client():
    def __init__(self, address=("127.0.0.1",5000)):
        self.socket = socket.socket()
        self.socket.connect(address)
        self.ops = [1,2,3,4]

    def do_op(self):
        # import random
        # random.randint(self.ops)
        self.send(" " * 2)
        self.send(OP_DATA_BEGIN)
        self.send(" " * 50)
        self.send(OP_DATA_END)
        self.send(" " * 3)

    def send(self, msg):
        data = bytearray(msg, "UTF-8") if msg != None else None
        if data != None:
            totalsent = 0
            while totalsent < len(data):
                sent = self.socket.send(data[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent
            print(" data has been sent successfully !")

tc=Client()
tc.do_op()
