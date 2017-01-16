import os
import sys
import time
import traceback

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from simple_host_target.client import Client
from simple_host_target.server import Server
from simple_host_target.definition import HOST_PORT, TARGET_PORT, HOST_PIPEIN_NAME,\
                        HOST_PIPEOUT_NAME, get_local_IP

class ExecutionHost(object):
    def __init__(self, IP):
        self.host_IP = IP
        self.target_IPs = set()
        self.used_target_IPs = set()

    def setup_target_IPs(self, target_IPs):
        assert(type(target_IPs) == set and len(target_IPs) > 0), "Must be a Set and size > 0."
        self.target_IPs = target_IPs

    def __ensure_target_IPs(self):
        if len(self.target_IPs) == 0:
            print("Empty target IPs, you should call setup_target_IPs before run !!")
            print("Or enter at least a valid Target IP ...")
            try:
                target_IP = ""
                for line in sys.stdin:
                    target_IP = line.strip()
                    break
                self.target_IPs.add(target_IP)
            except:
                print("Something wrong while processing target IP, exit !")
                sys.exit(1)

    def run(self):
        self.__ensure_target_IPs()
        self.server = Server(ip = self.host_IP, port = HOST_PORT)
        self.server.run_server(self.__recv_from_target)

        if not os.path.exists(HOST_PIPEIN_NAME):
            os.mkfifo(HOST_PIPEIN_NAME)

        print("Host is running ...")
        while 1:
            try:
                pipein = open(HOST_PIPEIN_NAME, 'rb')
                line = pipein.read()
                if len(line) != 0:
                    self.send_execution_task(line)
                time.sleep(1)
            except:
                traceback.print_exc()
                break
        self.__shutdown()

    def __shutdown(self):
        print("[Host] shutdown ... begin")
        if self.server:
            self.server.shutdown()
            self.server = None
        if os.path.exists(HOST_PIPEIN_NAME):
            os.unlink(HOST_PIPEIN_NAME)
        if os.path.exists(HOST_PIPEOUT_NAME):
            os.unlink(HOST_PIPEOUT_NAME)
        print("[Host] shutdown ... end")

    def __send_result(self, serialized_result_wrapper):
        if not os.path.exists(HOST_PIPEOUT_NAME):
            os.mkfifo(HOST_PIPEOUT_NAME)

        pipeout = os.open(HOST_PIPEOUT_NAME, os.O_WRONLY)
        os.write(pipeout, serialized_result_wrapper)
        os.close(pipeout)

    def __recv_from_target(self, serialized_result_wrapper):
        print("[Host] get result : %s "%(str(serialized_result_wrapper)))
        self.__send_result(serialized_result_wrapper)
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

def create_host():
    host_ip = get_local_IP()
    print("Creating host @(%s) ... are you sure ? Enter Yes/No."%(host_ip))
    try:
        for line in sys.stdin:
            msg = line.lower()
            if msg.find('yes') >= 0:
                host = ExecutionHost(host_ip)
                return host
            else:
                break
    except:
        traceback.print_exc()
    print("\r\nNothing created")
    return None

if __name__ == "__main__":
    host = create_host()
    if host:
        host.run()
