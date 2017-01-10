from op_code import OCLTaskExecutor, OCLTaskResult

class SimpleOCLTaskExecutor(OCLTaskExecutor):
    def __init__(self, info):
        OCLTaskExecutor.__init__(self)
        self.info = info

    def execute(self):
        import os
        print("[C][%d][SimpleOCLTaskExecutor] executing >>>>> "%(os.getpid()))
        task_result = OCLTaskResult(self.info)
        return task_result

def loads_and_execute(bytes_executor):
    import pickle
    executor = pickle.loads(bytes_executor)
    return executor.execute()
