import os
import sys
import socket

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from simple_host_target.definition import OP_HT_DATA_BEGIN, OP_HT_DATA_END,\
                                          OP_SH_DATA_PREFIX, OP_SH_DATA_POSTFIX,\
                                          OP_SH_DATA_MIDFIX

class Client(object):
    def __init__(self, ip = "127.0.0.1", port = 5000):
        self.socket = socket.socket()
        self.socket.connect((ip, port))

    def shutdown(self):
        if self.socket:
            print(" Client goes down ... ")
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None

    def send_sh_data(self, ip_port = "", serialized_task = ""):
        # Sample data to be sent !
        self.send(OP_SH_DATA_PREFIX)
        self.send(ip_port)
        self.send(OP_SH_DATA_MIDFIX)
        self.send(serialized_task)
        self.send(OP_SH_DATA_POSTFIX)

    def send_ht_data(self, serialized_wrapper = ""):
        # Sample data to be sent !
        self.send(OP_HT_DATA_BEGIN)
        self.send(serialized_wrapper)
        self.send(OP_HT_DATA_END)

    def send(self, msg):
        assert (self.socket != None)
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
    tc.send_ht_data()
    tc2.send_ht_data("THIS IS A TEST !!!")
    tc.shutdown()
    tc2.shutdown()
