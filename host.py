import sys
import pickle
from server import Server

class OCLExecutionHost(object):
    def __init__(self):
        self.server = Server(address = ("", 10000))
        self.server.run_server(self.__recv_from_target)
        pass

    def shutdown(self):
        print("[Host] shutdown ... begin")
        self.server.shutdown()
        print("[Host] shutdown ... end")

    def __recv_from_target(self, serialized_wrapper):
        result_wrapper = pickle.loads(serialized_wrapper)
        print("[Host] get result : %s "%(result_wrapper.get_result()))
        pass

    def send_execution_task(self, execute_wrapper):
        from client import Client
        c = Client()
        c.send_fake_data(execute_wrapper)

host = None
def create_host():
    print(" Create host ...")
    global host
    host = OCLExecutionHost()

def shutdown_host():
    print(" Shutdown host ... ")
    global host
    host.shutdown()

def send_execution_task(wrapper):
    print(" Send task ...")
    global host
    host.send_execution_task(wrapper)

if __name__ == "__main__":
    create_host()
    try:
        print("Press s + <Enter> to send a task !")
        for line in sys.stdin:
            if line == "s\n":
                from op_code import OCLExecutorWrapper
                from executor import SimpleOCLTaskExecutor, bytes_executor_loader
                executor_bytes = pickle.dumps(SimpleOCLTaskExecutor("Hello ..."))
                wrapper = OCLExecutorWrapper(executor_bytes, bytes_executor_loader)
                send_execution_task(wrapper)
    except:
        print("[Exception] when waiting for input !")
    finally:
        shutdown_host()
