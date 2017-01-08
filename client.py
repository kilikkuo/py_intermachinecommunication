import time
import socket
from op_code import OP_DATA_BEGIN, OP_DATA_END

class Client():
    def __init__(self, address=("127.0.0.1",5000)):
        self.socket = socket.socket()
        self.socket.connect(address)

    def send_fake_data(self):
        # Sample data to be sent !
        self.send(" " * 2)
        self.send(OP_DATA_BEGIN)
        self.send("ABCD" * 8196)
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
            print("%d bytes data has been sent successfully !"%(totalsent))

if __name__ == "__main__":
    tc=Client()
    tc.send_fake_data()
