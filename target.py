import pickle
import threading
from multiprocessing import Process, Pipe
from server import Server
from client import SimpleOCLTaskExecutor

def execute_task(task, conn):
    assert conn != None
    try:
        result = task.execute()
        conn.send(result)
    except:
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def launch_process(cb_to_target, task, parent_conn, child_conn):
    assert callable(cb_to_target)
    # Launch a python process to execute task.
    result = None
    try:
        p = Process(target=execute_task, args=(task, child_conn,))
        p.start()
        result = parent_conn.recv()
        p.join()
    except:
        result = None
        import traceback
        traceback.print_exc()
    finally:
        cb_to_target(result)

class OCLExecutionTarget:
    def __init__(self):
        # max_client should always be 1 (OCLTaskHost)
        self.server = Server(max_client = 1)
        self.parent_conn, self.child_conn = Pipe()
        pass

    def start(self):
        self.server.run_server(self.__task_package_callback)
        pass

    def __recv_from_executor(self, ocl_result):
        print("[P] result : %s "%(str(ocl_result)))
        pickled_result = pickle.dumps(ocl_result)
        # TODO : Send this pickled OCLTaskResult back to Host.
        pass

    def __task_package_callback(self, package_bytes):
        thread = None
        try:
            task = pickle.loads(package_bytes)
            thread = threading.Thread(target=launch_process,
                                      args=(self.__recv_from_executor,
                                            task,
                                            self.parent_conn,
                                            self.child_conn))
            thread.daemon = True
            thread.start()
        except:
            import traceback
            traceback.print_exc()
        finally:
            if thread:
                thread.join()

if __name__ == "__main__":
    target = OCLExecutionTarget()
    target.start()
