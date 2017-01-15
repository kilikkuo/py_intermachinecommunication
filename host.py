import os
import sys
import time
import pickle
from server import Server
from definition import HOST_PORT, HOST_IP, TARGET_PORT, HOST_PIPEIN_NAME,\
                       HOST_PIPEOUT_NAME

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
        print("[Host] get result : %s "%(str(serialized_result_wrapper)))
        send_result(serialized_result_wrapper)
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

def send_result(serialized_result_wrapper):
    if not os.path.exists(HOST_PIPEOUT_NAME):
        os.mkfifo(HOST_PIPEOUT_NAME)

    pipeout = os.open(HOST_PIPEOUT_NAME, os.O_WRONLY)
    os.write(pipeout, serialized_result_wrapper)
    os.close(pipeout)

host = None
def create_host():
    print(" Create host ...")
    global host
    host = ExecutionHost()

    if not os.path.exists(HOST_PIPEIN_NAME):
        os.mkfifo(HOST_PIPEIN_NAME)

    while 1:
        try:
            pipein = open(HOST_PIPEIN_NAME, 'rb')
            line = pipein.read()
            if len(line) != 0:
                host.send_execution_task(line)
            time.sleep(1)
        except:
            break

def shutdown_host():
    print(" Shutdown host ... ")
    global host
    host.shutdown()
    if os.path.exists(HOST_PIPEIN_NAME):
        os.unlink(HOST_PIPEIN_NAME)
    if os.path.exists(HOST_PIPEOUT_NAME):
        os.unlink(HOST_PIPEOUT_NAME)

if __name__ == "__main__":
    try:
        create_host()
    except:
        import traceback
        traceback.print_exc()
        print("[Exception] when waiting for input !")
    finally:
        shutdown_host()
