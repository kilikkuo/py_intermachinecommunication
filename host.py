import sys
import pickle
from server import Server
from definition import HOST_PORT, HOST_IP, TARGET_PORT

class ExecutionHost(object):
    def __init__(self):
        self.server = Server(ip = HOST_IP, port = HOST_PORT)
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
        # TODO : Select one of Target to send task
        c = Client(port = TARGET_PORT)
        c.send_fake_data(execute_wrapper)

host = None
def create_host():
    print(" Create host ...")
    global host
    host = ExecutionHost()

def shutdown_host():
    print(" Shutdown host ... ")
    global host
    host.shutdown()

def send_execution_task():
    print(" Send task ...")
    global host
    from definition import ExecutorWrapper
    from executor import SimpleTaskExecutor, bytes_executor_loader
    executor_bytes = pickle.dumps(SimpleTaskExecutor("Hello ..."))
    wrapper = ExecutorWrapper(executor_bytes, bytes_executor_loader)
    host.send_execution_task(wrapper)

if __name__ == "__main__":
    create_host()
    try:
        print("Press s + <Enter> to send a task !")
        for line in sys.stdin:
            if line == "s\n":
                send_execution_task()
    except:
        print("[Exception] when waiting for input !")
        import traceback
        traceback.print_exc()
    finally:
        shutdown_host()
