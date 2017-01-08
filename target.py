import abc
import threading
from multiprocessing import Process, Pipe
from server import Server

class OCLTaskResult:
    def __init__(self, result):
        self.result = result

    def get_result(self):
        return self.result

class OCLTaskExecutor(object):
    def __init__(self, package_bytes):
        self.package_bytes = package_bytes

    def execute(self):
        import os
        print("[C][%d][OCLTaskExecutor] executing >>>>> "%(os.getpid()))
        task_result = OCLTaskResult("Hello")
        return task_result

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
        # TODO : Send this OCLTaskResult back to Host.
        pass

    def __task_package_callback(self, package_bytes):
        # TODO : Need to wrap package_bytes into OCLTask
        task = OCLTaskExecutor(package_bytes)

        thread = threading.Thread(target=launch_process,
                                  args=(self.__recv_from_executor,
                                        task,
                                        self.parent_conn,
                                        self.child_conn))
        thread.daemon = True
        thread.start()
        thread.join()

if __name__ == "__main__":
    target = OCLExecutionTarget()
    target.start()
