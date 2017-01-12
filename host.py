import os
import sys
import time
import pickle
from server import Server
from definition import HOST_PORT, HOST_IP, TARGET_PORT, HOST_PIPE_NAME

class ExecutionHost(object):
    def __init__(self):
        self.server = Server(ip = HOST_IP, port = HOST_PORT)
        self.server.run_server(self.__recv_from_target)
        pass

    def shutdown(self):
        print("[Host] shutdown ... begin")
        self.server.shutdown()
        print("[Host] shutdown ... end")

    def __recv_from_target(self, serialized_result_wrapper):
        # TODO : Need to pass serialized_wrapper back to project_sender
        result_wrapper = pickle.loads(serialized_result_wrapper)
        print("[Host] get result : %s "%(result_wrapper.get_result()))
        pass

    def send_execution_task(self, execute_wrapper):
        from client import Client
        # TODO : Select one of Target to send task
        c = None
        try:
            c = Client(port = TARGET_PORT)
            c.send_data(execute_wrapper)
        except:
            import traceback
            traceback.print_exc()
            print("[Host][Exception] while sending execution task !")
        finally:
            if c:
                c.shutdown()

host = None
def create_host():
    print(" Create host ...")
    global host
    host = ExecutionHost()

    if not os.path.exists(HOST_PIPE_NAME):
        os.mkfifo(HOST_PIPE_NAME)

    totalline = b''
    while True:
        pipein = open(HOST_PIPE_NAME, 'rb')
        print("Press s + <Enter> to send a task !")
        line = pipein.read()
        if len(line) != 0:
            host.send_execution_task(line)
        time.sleep(1)

def shutdown_host():
    print(" Shutdown host ... ")
    global host
    host.shutdown()

if __name__ == "__main__":
    try:
        create_host()
    except:
        import traceback
        traceback.print_exc()
        print("[Exception] when waiting for input !")
    finally:
        shutdown_host()
