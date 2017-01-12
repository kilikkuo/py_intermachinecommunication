import sys
import pickle
from multiprocessing import Process, Pipe
from server import Server
from definition import HOST_IP, HOST_PORT, TARGET_PORT

def execute_task(serialized_wrapper, conn):
    print(" >>>>> Going to execute task !!")
    assert conn != None
    try:
        wrapper = pickle.loads(serialized_wrapper)
        result = wrapper.execute()
        conn.send(result)
    except:
        import traceback
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
        import traceback
        traceback.print_exc()
    finally:
        cb_to_target(result)

class ExecutionTarget(object):
    def __init__(self):
        # max_client should always be 1 (TaskHost)
        self.server = Server(port = TARGET_PORT, max_client = 1)
        self.parent_conn, self.child_conn = Pipe()
        self.thread = None
        pass

    def shutdown(self):
        if self.thread:
            self.thread.join()
            self.thread = None
        if self.server:
            self.server.shutdown()

    def run_until_exception(self):
        self.server.run_server(self.__task_package_callback)
        try:
            import time
            while 1:
                time.sleep(1)
        except:
            import traceback
            traceback.print_exc()
            print("[Target][Exception] while lining in ")
        finally:
            self.shutdown()
        pass

    def __recv_from_executor(self, serialized_result_wrapper):
        print("[Target][P] result : %s "%(str(serialized_result_wrapper)))
        from client import Client
        c = None
        try:
            c = Client(ip = HOST_IP, port = HOST_PORT)
            c.send_data(serialized_result_wrapper)
        except:
            import traceback
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
        self.thread = None
        try:
            import threading
            self.thread = threading.Thread(target=launch_process,
                                           args=(self.__recv_from_executor,
                                                 serialized_executor_wrapper,
                                                 self.parent_conn,
                                                 self.child_conn))
            self.thread.daemon = True
            self.thread.start()
        except:
            import traceback
            traceback.print_exc()
        finally:
            pass
            if self.thread:
                print("[Target] self.thread.join() begin ")
                self.thread.join()
                print("[Target] self.thread.join() end ")
                self.thread = None

if __name__ == "__main__":
    print(" Create target ...")
    target = ExecutionTarget()
    target.run_until_exception()
