import os
import sys
import time
import pickle
import threading
import traceback

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from simple_host_target.client import Client
from simple_host_target.server import Server
from simple_host_target.definition import HOST_PORT, TARGET_PORT,\
                        get_local_IP, OP_SH_DATA_PREFIX,\
                        OP_SH_DATA_POSTFIX, OP_SH_DATA_MIDFIX
from simple_host_target.generaltaskthread import TaskThread, Task

class ResultJob2SenderTask(Task):
    def __init__(self, host, serialized_result_wrapper):
        Task.__init__(self)
        self.host = host
        self.serialized_result_wrapper = serialized_result_wrapper

    def run(self):
        print("[Host][Thread] sending result to sender !")
        c = None
        try:
            rw = pickle.loads(self.serialized_result_wrapper)
            sh_ip_pairs = self.host.dicToken2Pairs.pop(rw.token, "")
            used_target_ip = self.host.dicTokenIP.pop(rw.token, None)
            assert used_target_ip != None
            self.host.return_target_ip(used_target_ip)

            sender_ip = sh_ip_pairs.get("sender_ip", "")
            sender_port = sh_ip_pairs.get("sender_port", 0)
            c = Client(ip = sender_ip, port = sender_port)
            c.send_sh_data("", self.serialized_result_wrapper)
        except:
            traceback.print_exc()
            print("[Host][Thread][Exception] while sending result task !")
        finally:
            if c:
                c.shutdown()

class ExecJob2TargetTask(Task):
    def __init__(self, host, target_ip, ip_port_pairs, serialized_executor_wrapper):
        Task.__init__(self)
        self.host = host
        self.target_ip = target_ip
        self.ip_port_pairs = ip_port_pairs
        self.serialized_executor_wrapper = serialized_executor_wrapper
        pass

    def run(self):
        print("[Host][Thread] sending task to target !")
        c = None
        try:
            ew = pickle.loads(self.serialized_executor_wrapper)
            c = Client(ip = self.target_ip, port = TARGET_PORT)
            c.send_ht_data(self.serialized_executor_wrapper)
            self.host.dicTokenIP[ew.token] = self.target_ip
            self.host.dicToken2Pairs[ew.token] = self.ip_port_pairs
        except:
            traceback.print_exc()
            print("[Host][Thread][Exception] while sending execution task !")
        finally:
            if c:
                c.shutdown()

class ExecutionHost(object):
    def __init__(self, IP):
        self.host_IP = IP
        self.target_IPs = set()
        self.dicTokenIP = {}
        self.dicToken2Pairs = {}
        self.pendings = []
        self.lock = threading.Lock()
        self.thread = TaskThread(name = "host_thread")
        self.thread.daemon = True
        self.thread.start()

    def setup_target_IPs(self, target_IPs):
        assert(type(target_IPs) == list and len(target_IPs) > 0), "Must be a list and size > 0."
        self.target_IPs = set(target_IPs)

    def __ensure_target_IPs(self):
        if len(self.target_IPs) == 0:
            print("Empty target IPs, you should call setup_target_IPs before run !!")
            print("Enter at least one Target IP or a list of IPs, e.g. 1.1.1.1, 2.3.3.4, 2.1.5.6")
            print("... or enter yes to use host's IP")
            try:
                target_IPs = sys.stdin.readline()
                if "yes" in target_IPs.strip():
                    target_IP = self.host_IP
                    self.target_IPs.add(target_IP)
                else:
                    IPs = target_IPs.split(",")
                    for ip in IPs:
                        self.target_IPs.add(ip.strip())
            except:
                print("Something wrong while processing target IP, exit !")
                sys.exit(1)

    def run(self):
        self.__ensure_target_IPs()
        self.server = Server(ip = self.host_IP, port = HOST_PORT)
        self.server.run_server(self.__recv_from_target,
                               callback_info = { 1 : { "pre"   : OP_SH_DATA_PREFIX,
                                                       "post"  : OP_SH_DATA_POSTFIX,
                                                       "mid"   : OP_SH_DATA_MIDFIX,
                                                       "callback" : self.__recv_from_sender
                                                     }
                                               })

        print("Host is running ...")
        while 1:
            try:
                time.sleep(0.01)
            except:
                traceback.print_exc()
                break
        self.__shutdown()

    def __shutdown(self):
        print("[Host] shutdown ... begin")
        if len(self.pendings):
            print("[Host][Warning] pending jobs are gonna be dropped !")
            self.pendings = []
        if self.thread:
            self.thread.stop()
            self.thread = None
        if self.server:
            self.server.shutdown()
            self.server = None
        print("[Host] shutdown ... end")

    def retrieve_target_ip(self):
        with self.lock:
            t_ip = self.target_IPs.pop() if len(self.target_IPs) else None
            return t_ip

    def return_target_ip(self, ip):
        with self.lock:
            self.target_IPs.add(ip)
        self.__retrigger_pending_jobs()

    def __retrigger_pending_jobs(self):
        if len(self.pendings):
            t_ip = self.retrieve_target_ip()
            if t_ip != None:
                dict_IP_pairs, serialized_executor_wrapper = self.pendings.pop(0)
                job = ExecJob2TargetTask(self, t_ip, dict_IP_pairs, serialized_executor_wrapper)
                self.thread.addtask(job)

    def __recv_from_sender(self, ip_port_pairs, serialized_executor_wrapper):
        dict_IP_pairs = eval(ip_port_pairs.decode("ASCII"))

        t_ip = self.retrieve_target_ip()
        if t_ip == None:
            print("No available target for new job. Will try later !!")
            self.pendings.append((dict_IP_pairs, serialized_executor_wrapper))
            return

        job = ExecJob2TargetTask(self, t_ip, dict_IP_pairs, serialized_executor_wrapper)
        self.thread.addtask(job)

    def __recv_from_target(self, serialized_result_wrapper):
        print("[Host] get result : %s "%(str(serialized_result_wrapper)))

        job = ResultJob2SenderTask(self, serialized_result_wrapper)
        self.thread.addtask(job)

def create_host():
    host_ip = get_local_IP()
    print("Creating host @(%s) ... Proceed (yes/no)?"%(host_ip))
    try:
        msg = sys.stdin.readline()
        if msg.lower().find('yes') >= 0:
            host = ExecutionHost(host_ip)
            return host
    except:
        traceback.print_exc()
    print("Nothing created")
    return None

if __name__ == "__main__":
    host = create_host()
    if host:
        host.run()
