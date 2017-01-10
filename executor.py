import os
import pickle
from op_code import OCLTaskExecutor, OCLTaskResult, OCLResultWrapper

def bytes_result_loader(bytes_result):
    result = pickle.loads(bytes_result)
    return result.get_result()

def bytes_executor_loader(bytes_executor):
    executor = pickle.loads(bytes_executor)
    return executor.execute()

class SimpleOCLTaskResult(OCLTaskResult):
    def __init__(self, package):
        OCLTaskResult.__init__(self)
        self.package = package

    def get_result(self):
        # Do whatever to the package to make it start working !
        print("[C][%d][SimpleOCLTaskResult] get_result >>>>> "%(os.getpid()))
        return self.package

class SimpleOCLTaskExecutor(OCLTaskExecutor):
    def __init__(self, package):
        OCLTaskExecutor.__init__(self)
        self.package = package

    def execute(self):
        # Do whatever to the package to make it start working !
        print("[C][%d][SimpleOCLTaskExecutor] executing >>>>> "%(os.getpid()))
        bytes_result = pickle.dumps(SimpleOCLTaskResult("AABBCC Result!"))
        wrapper = OCLResultWrapper(bytes_result, bytes_result_loader)
        return wrapper
