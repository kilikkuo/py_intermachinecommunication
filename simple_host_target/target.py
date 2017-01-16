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
from simple_host_target.definition import HOST_PORT, TARGET_PORT, get_local_IP

def execute_task(serialized_wrapper, conn):
    print(" >>>>> Going to execute task !!")
    assert conn != None
    try:
        wrapper = pickle.loads(serialized_wrapper)
        result = wrapper.execute()
        conn.send(result)
    except:
        traceback.print_exc()
    finally:
        conn.close()

def launch_process(cb_to_target, wrapper, parent_conn, child_conn):
    assert callable(cb_to_target)
    # Launch a python process to execute task.
    result = None
    try:
        p = Process(target=execute_task, args=(wrapper, child_conn,))
        p.start()
        print(" >>>>> Process launched !!")
        result = parent_conn.recv()
        p.join()
    except:
        result = None
        traceback.print_exc()
    finally:
        cb_to_target(result)

class ExecutionTarget(object):
    def __init__(self, target_IP):
        self.host_IP = ""
        self.target_IP = target_IP
        self.parent_conn, self.child_conn = Pipe()
        pass

    def __shutdown(self):
        if self.server:
            self.server.shutdown()

    def __ensure_host_IP(self, IP):
        if IP == "":
            print("Empty host IP !, Please enter a valid Host IP ...")
            try:
                for line in sys.stdin:
                    processed_IP = line.strip()
                    break
                return processed_IP
            except:
                print("Something wrong while processing host IP, exit !")
                sys.exit(1)
        return IP

    def run_until_exception(self, host_IP):
        self.host_IP = self.__ensure_host_IP(host_IP)
        # TODO: max_client should always be 1 (TaskHost)
        self.server = Server(ip = self.target_IP, port = TARGET_PORT, max_client = 1)
        self.server.run_server(self.__task_package_callback)
        try:
            # CAUTION : Using sys.stdin will result in hang while spawning
            #           process.
            print("Target is running ...")
            import time
            while 1:
                time.sleep(1)
        except:
            print("[Target][Exception] while lining in ")
        finally:
            self.__shutdown()
        pass

    def __recv_from_executor(self, serialized_result_wrapper):
        print("[Target][P] result : %s "%(str(serialized_result_wrapper)))
        c = None
        try:
            c = Client(ip = self.host_IP, port = HOST_PORT)
            c.send_data(serialized_result_wrapper)
        except:
            traceback.print_exc()
            print("[Target][P][Exception] while receiving result from executor !")
        finally:
            if c:
                c.shutdown()

    def __task_package_callback(self, serialized_executor_wrapper):
        print("[Target] __task_package_callback .... >>>> ")
        if len(serialized_executor_wrapper) == 0:
            print("No package bytes !! ")
            return
        thread = None
        try:
            thread = threading.Thread(target=launch_process,
                                      args=(self.__recv_from_executor,
                                            serialized_executor_wrapper,
                                            self.parent_conn,
                                            self.child_conn))
            thread.daemon = True
            thread.start()
        except:
            traceback.print_exc()
        finally:
            pass
            if thread:
                print("[Target][Thread for Process] join begin ")
                thread.join()
                print("[Target][Thread for Process] join end ")
                thread = None

# Exported function
def create_target():
    target_ip = get_local_IP()
    print("Creating target @(%s) ... are you sure ? Enter Yes/No."%(target_ip))
    try:
        for line in sys.stdin:
            msg = line.lower().strip()
            if msg.find('yes') >= 0:
                return ExecutionTarget(target_ip)
            else:
                break
    except:
        traceback.print_exc()
    print("\r\nNothing created")
    return None

if __name__ == "__main__":
    target = create_target()
    if target:
        target.run_until_exception("")
