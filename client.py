import time
import socket
import pickle
from op_code import OP_DATA_BEGIN, OP_DATA_END, OCLTaskExecutor, OCLTaskResult

class SimpleOCLTaskExecutor(OCLTaskExecutor):
    def __init__(self, package_bytes):
        OCLTaskExecutor.__init__(self, package_bytes)

    def execute(self):
        import os
        print("[C][%d][SimpleOCLTaskExecutor] executing >>>>> "%(os.getpid()))
        task_result = OCLTaskResult("Hello")
        return task_result

class Client():
    def __init__(self, address=("127.0.0.1",5000)):
        self.socket = socket.socket()
        self.socket.connect(address)

    def send_fake_data(self):
        # Sample data to be sent !
        self.send(" " * 2)
        self.send(OP_DATA_BEGIN)
        executor = SimpleOCLTaskExecutor("executor ...")
        data = pickle.dumps(executor)
        self.send(data)
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
    tc=Client()
    # tc2=Client()
    # tc3=Client()
    tc.send_fake_data()
    # tc2.send_fake_data()
    # tc3.send_fake_data()
