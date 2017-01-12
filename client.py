import socket
import pickle
from definition import OP_DATA_BEGIN, OP_DATA_END

class Client(object):
    def __init__(self, ip = "127.0.0.1", port = 5000):
        self.socket = socket.socket()
        self.socket.connect((ip, port))

    def shutdown(self):
        if self.socket:
            print(" Client goes down ... ")
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()

    def send_data(self, wrapper = None):
        # Sample data to be sent !
        self.send(" " * 2)
        self.send(OP_DATA_BEGIN)
        self.send(wrapper)
        self.send(OP_DATA_END)
        self.send(" " * 3)

    def send(self, msg):
        data = bytearray(msg, "ASCII") if msg != None and type(msg) == str else msg
        if data != None:
            totalsent = 0
            while totalsent < len(data):
                sent = self.socket.send(data[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent
            print("%d bytes data has been sent successfully !"%(totalsent))

if __name__ == "__main__":
    tc = Client()
    tc2 = Client()
    tc.send_data()
    tc2.send_data("THIS IS A TEST !!!")
    tc.shutdown()
    tc2.shutdown()
