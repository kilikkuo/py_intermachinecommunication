import os
import pickle
from op_code import TaskExecutor, TaskResult, ResultWrapper

def bytes_result_loader(bytes_result):
    result = pickle.loads(bytes_result)
    return result.get_result()

def bytes_executor_loader(bytes_executor):
    executor = pickle.loads(bytes_executor)
    return executor.execute()

class SimpleTaskResult(TaskResult):
    def __init__(self, package):
        TaskResult.__init__(self)
        self.package = package

    def get_result(self):
        # Do whatever to the package to make it start working !
        print("[C][%d][SimpleTaskResult] get_result >>>>> "%(os.getpid()))
        return self.package

class SimpleTaskExecutor(TaskExecutor):
    def __init__(self, package):
        TaskExecutor.__init__(self)
        self.package = package

    def execute(self):
        # Do whatever to the package to make it start working !
        print("[C][%d][SimpleTaskExecutor] executing >>>>> "%(os.getpid()))
        bytes_result = pickle.dumps(SimpleTaskResult("AABBCC Result!"))
        wrapper = ResultWrapper(bytes_result, bytes_result_loader)
        return wrapper
