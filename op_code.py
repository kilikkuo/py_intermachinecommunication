from abc import ABCMeta, abstractmethod
import pickle

OP_DATA_BEGIN       = "DTBegin"
OP_DATA_END         = "DTEnd"

class OCLTaskResult:
    # Should sub-class this class as your own specific Result
    # See SimpleOCLTaskResult in executor.py
    __metaclass__ = ABCMeta
    @abstractmethod
    def get_result(self):
        raise NotImplemented("Not implemented !")

class OCLResultWrapper:
    def __init__(self, bytes_result, bytes_result_loader):
        # A bytesArray which represents the serialized result.
        self.bytes_result = bytes_result
        # The loader to help you recover the serialized result and
        # get actual result back !
        self.bytes_result_loader = bytes_result_loader

    def get_result(self):
        return self.bytes_result_loader(self.bytes_result)

class OCLTaskExecutor(object):
    # Should sub-class this class as your own specific Execution
    # See SimpleOCLTaskExecutor in executor.py
    __metaclass__ = ABCMeta
    @abstractmethod
    def execute(self):
        raise NotImplemented("Not implemented !")

class OCLExecutorWrapper(object):
    def __init__(self, bytes_executor, bytes_executor_loader):
        # A bytesArray which represents the serialized executor.
        self.bytes_executor = bytes_executor
        # The loader to help you recover the serialized executor and
        # execute it !
        self.bytes_executor_loader = bytes_executor_loader

    def execute(self):
        return self.bytes_executor_loader(self.bytes_executor)
