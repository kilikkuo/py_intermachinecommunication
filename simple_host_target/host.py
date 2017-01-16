import os
import sys
import time
import traceback

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from simple_host_target.client import Client
from simple_host_target.server import Server
from simple_host_target.definition import HOST_PORT, HOST_IP, TARGET_PORT, HOST_PIPEIN_NAME,\
                        HOST_PIPEOUT_NAME, get_local_IP

class ExecutionHost(object):
    def __init__(self, host_ip = HOST_IP, target_IPs = []):
        self.server = Server(ip = host_ip, port = HOST_PORT)
        self.server.run_server(self.__recv_from_target)
        self.target_IPs = set(target_IPs)
        self.used_target_IPs = set()
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
        # TODO : Select one of Target to send task
        t_ip = self.target_IPs.pop() if len(self.target_IPs) else None
        if t_ip == None:
            print("No available target for new job. Try later !!")
            return
        c = None
        try:
            c = Client(ip = t_ip, port = TARGET_PORT)
            c.send_data(execute_wrapper)
        except:
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
def create_host(h_IP, t_IPs):
    global host
    assert (host == None)
    print(" Create host ... @(%s)"%(h_IP))
    host = ExecutionHost(h_IP, t_IPs)

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
            traceback.print_exc()
            break

def shutdown_host():
    print(" Shutdown host ... ")
    global host
    assert (host != None)
    host.shutdown()
    if os.path.exists(HOST_PIPEIN_NAME):
        os.unlink(HOST_PIPEIN_NAME)
    if os.path.exists(HOST_PIPEOUT_NAME):
        os.unlink(HOST_PIPEOUT_NAME)
    host = None

# Exported function
def launch_host(IP = None, target_IPs = []):
    try:
        host_IP = IP if IP else get_local_IP()
        create_host(host_IP, target_IPs)
    except:
        traceback.print_exc()
        print("[Exception] when waiting for input !")
    finally:
        shutdown_host()

if __name__ == "__main__":
    launch_host(get_local_IP(), [get_local_IP()])
