import os
import sys
import pickle
import traceback
import threading
from multiprocessing import Process, Pipe

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from simple_host_target.client import Client
from simple_host_target.server import Server
from simple_host_target.definition import HOST_PORT, TARGET_PORT, get_local_IP,\
                                        OP_HT_DATA_BEGIN, OP_HT_DATA_END,\
                                        OP_HT_DATA_MID, ResultWrapper
from simple_host_target.generaltaskthread import TaskThread, Task

def execute_task(serialized_wrapper, conn):
    print(" >>>>> Going to execute task !!")
    assert conn != None
    try:
        wrapper = pickle.loads(serialized_wrapper)
        result_bitstream = wrapper.execute()
        result_wrapper = ResultWrapper(wrapper.token, result_bitstream)
        serialized_result_wrapper = pickle.dumps(result_wrapper)
        conn.send(serialized_result_wrapper)
    except:
        traceback.print_exc()
    finally:
        conn.close()

def launch_process(cb_to_target, wrapper):
    assert callable(cb_to_target)
    # Launch a python process to execute task.
    result = None
    try:
        p_conn, c_conn = Pipe()
        p = Process(target=execute_task, args=(wrapper, c_conn,))
        p.start()
        print(" >>>>> Process launched !!")
        result = p_conn.recv()
        p.join()
    except:
        result = None
        traceback.print_exc()
    finally:
        cb_to_target(result)

class SpawnExecuteTask(Task):
    def __init__(self, recv_from_executor, serialized_wrapper):
        Task.__init__(self)
        self.recv_cb = recv_from_executor
        self.serialized_wrapper = serialized_wrapper
        pass
    def run(self):
        launch_process(self.recv_cb, self.serialized_wrapper)
        pass

class SendResultToHost(Task):
    def __init__(self, host_ip, host_port, serialized_result_wrapper):
        Task.__init__(self)
        self.ip = host_ip
        self.port = host_port
        self.serialized_result_wrapper = serialized_result_wrapper

    def run(self):
        c = None
        try:
            c = Client(ip = self.ip, port = self.port)
            c.send_ht_data(self.serialized_result_wrapper)
        except:
            traceback.print_exc()
            print("[Target][P][SendResultToHost][Exception] !")
        finally:
            if c:
                c.shutdown()

class ExecutionTarget(object):
    def __init__(self, target_IP):
        self.host_IP = ""
        self.target_IP = target_IP
        self.thread = TaskThread(name="target_thread")
        self.thread.daemon = True
        self.thread.start()
        pass

    def __shutdown(self):
        if self.thread:
            self.thread.stop()
        if self.server:
            self.server.shutdown()

    def __ensure_host_IP(self, IP):
        if IP == "":
            print("Empty host IP !, Please enter a valid Host IP ...")
            print("Or enter yes to use target's IP.")
            try:
                msg = sys.stdin.readline()
                if msg.lower().strip().find('yes') >= 0:
                    processed_IP = self.target_IP
                else:
                    processed_IP = msg.lower().strip()
                    assert len(processed_IP.split(".")) == 4
                return processed_IP
            except:
                print("Something wrong while processing host IP, exit !")
                sys.exit(1)
        return IP

    def run(self, host_IP = ""):
        self.host_IP = self.__ensure_host_IP(host_IP)
        # TODO: max_client should always be 1 (TaskHost)
        self.server = Server(ip = self.target_IP, port = TARGET_PORT, max_client = 1)
        self.server.run_server(callbacks_info = { 0 : { "pre" : OP_HT_DATA_BEGIN,
                                                        "post": OP_HT_DATA_END,
                                                        "mid" : OP_HT_DATA_MID,
                                                        "callback"  : self.__recv_from_host }})
        try:
            # CAUTION : Using sys.stdin will result in hang while spawning
            #           process.
            print("Target is running ...")
            import time
            while 1:
                time.sleep(0.01)
        except:
            print("[Target][Exception] while lining in ")
        finally:
            self.__shutdown()
        pass

    def __recv_from_executor(self, serialized_result_wrapper):
        print("[Target][P] result : %s "%(str(serialized_result_wrapper)))
        task = SendResultToHost(self.host_IP, HOST_PORT, serialized_result_wrapper)
        self.thread.addtask(task)

    def __recv_from_host(self, serialized_executor_wrapper):
        print("[Target] __recv_from_host .... >>>> ")
        if len(serialized_executor_wrapper) == 0:
            print("No package bytes !! ")
            return
        try:
            task = SpawnExecuteTask(self.__recv_from_executor,
                                    serialized_executor_wrapper)
            self.thread.addtask(task)
        except:
            traceback.print_exc()

# Exported function
def create_target():
    target_ip = get_local_IP()
    print("Creating target @(%s) ... Proceed (yes/no)?"%(target_ip))
    try:
        msg = sys.stdin.readline()
        if msg.lower().strip().find('yes') >= 0:
            return ExecutionTarget(target_ip)
    except:
        traceback.print_exc()
    print("Nothing created")
    return None

if __name__ == "__main__":
    target = create_target()
    if target:
        target.run()
