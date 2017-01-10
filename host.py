import sys
import threading
import pickle
from op_code import OCLTaskWrapper
from server import Server

class OCLExecutionHost(object):
    def __init__(self):
        self.server = Server(address = ("", 10000))
        self.server.run_server(self.__recv_from_target)
        self.clients = {}
        pass

    def shutdown(self):
        print("[Host] shutting down ... ")
        self.server.shutdown()
        print("[Host] shutting down ... end")

    def __recv_from_target(self, result):
        print("OCLExecutionHost: %s "%(str(result)))
        pass

    def send_task(self):
        from client import Client
        c = Client()
        from executor import SimpleOCLTaskExecutor, loads_and_execute
        executor_bytes = pickle.dumps(SimpleOCLTaskExecutor("Hello ..."))
        wrapper = OCLTaskWrapper(executor_bytes, loads_and_execute)
        c.send_fake_data(wrapper)

host = None
def create_host():
    print(" Create ... host")
    global host
    host = OCLExecutionHost()

def shutdown_host():
    print(" Shutdown ... host")
    global host
    host.shutdown()

def send_task():
    print(" Send task ...")
    global host
    host.send_task()

if __name__ == "__main__":
    create_host()
    try:
        for line in sys.stdin:
            print(line)
            if line == "send_task\n":
                send_task()
    except:
        print("exception line in ")
    finally:
        shutdown_host()
