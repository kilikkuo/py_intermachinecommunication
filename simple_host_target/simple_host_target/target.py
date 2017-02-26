import os
import sys
import time
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

class WPExecutorTask(Task):
    def __init__(self, target_func, wrapper, conn):
        Task.__init__(self)
        self.target_func = target_func
        self.executor_wrapper = wrapper
        self.conn = conn

    def run(self):
        print("[WP][ExecutorTask] is running ....")
        time.sleep(5)
        self.target_func(self.executor_wrapper, self.conn)

class WorkerProcess(Process):
    def __init__(self, target_func, wrapper, conn):
        Process.__init__(self)
        self.target_func = target_func
        self.conn = conn
        self.wrapper = wrapper

    def run(self):
        print("[WP] is running ....")
        import time
        proc_name = self.name

        thread = TaskThread(name="[WP][WorkerThread]")
        thread.start()
        # Create the executor task to load script.
        wpe_task = WPExecutorTask(self.target_func, self.wrapper, self.conn)
        thread.addtask(wpe_task)

        # This while loop is to read command from sender.
        # TODO : deliver this command to WPExecutorTask
        while True:
            time.sleep(0.01)
            if self.conn.poll():
                msg = self.conn.recv()
                print("[WP] received msg(%s)"%(msg))
        return

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

class MonitorWorkerTask(Task):
    def __init__(self, t_conn, callback, evt):
        Task.__init__(self)
        self.t_conn = t_conn
        self.callback = callback
        self.evt = evt

    def run(self):
        print("[TP][Monitor] monitoring ... ")
        while True:
            time.sleep(0.01)
            if self.evt.is_set():
                print("[TP][Monitor] stop monitoring ... ")
                break
            # Receiving results from Worker Process, and callback to Target
            if self.t_conn and self.t_conn.poll():
                msg = self.t_conn.recv()
                print("[TP] received result from WP : %s"%(msg))
                self.callback(msg)

class ExecutionTarget(object):
    def __init__(self, target_IP):
        self.host_IP = ""
        self.target_IP = target_IP
        self.t_conn, self.w_conn = None, None

        self.monitor_break_evt = threading.Event()

        self.thread = TaskThread(name="target_thread")
        self.thread.daemon = True
        self.thread.start()
        self.monitor = TaskThread(name = "monitor_thread")
        self.monitor.daemon = True
        self.monitor.start()

        self.worker_process = None
        pass

    def __shutdown(self):
        if self.thread:
            self.thread.stop()
        if self.monitor:
            self.monitor_break_evt.set()
            time.sleep(0.5)
            self.monitor.stop()
        if self.server:
            self.server.shutdown()
        self.thread = None
        self.monitor = None
        self.server = None

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

    def __terminate_worker_and_monitor(self):
        if self.worker_process and self.worker_process.is_alive():
            print("[Target][P] terminating worker process ... ")
            self.monitor_break_evt.set()
            self.w_conn.close()
            self.w_conn = None
            self.t_conn.close()
            self.t_conn = None
            self.worker_process.terminate()
            self.worker_process = None

    def __recv_from_executor(self, serialized_result_wrapper):
        print("[Target][P] result : %s "%(str(serialized_result_wrapper)))
        task = SendResultToHost(self.host_IP, HOST_PORT, serialized_result_wrapper)
        self.thread.addtask(task)
        self.__terminate_worker_and_monitor()

    def __recv_from_host(self, info_package):
        #        { "cmd" : "XXX",
        #          "sew" : serialized_executor_wrapper}
        print("[Target] __recv_from_host .... >>>>")
        if len(info_package) == 0:
            print("No package bytes !! ")
            return
        try:
            if self.t_conn == None and self.w_conn == None:
                self.t_conn, self.w_conn = Pipe()
                self.monitor_break_evt.clear()
                self.monitor.addtask(MonitorWorkerTask(self.t_conn,
                                                       self.__recv_from_executor,
                                                       self.monitor_break_evt))
            assert self.t_conn != None and self.w_conn != None

            info = eval(info_package)
            command = info.get("cmd", "")
            serialized_executor_wrapper = info.get("sew", "")
            print("[Target] recv - cmd(%s) / sew(%s)"%(command, serialized_executor_wrapper))
            if command and self.worker_process:
                self.t_conn.send(command)
            elif self.worker_process == None:
                self.worker_process = WorkerProcess(execute_task,
                                                    serialized_executor_wrapper,
                                                    self.w_conn)
                self.worker_process.start()
                print(" >>>>> Worker Process launched !!")
            else:
                assert False, "Not supported yet !!"
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
