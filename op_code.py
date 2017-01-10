from abc import ABCMeta, abstractmethod
import pickle

OP_CONNECTION_BEGIN = "CNXBegin"
OP_DATA_BEGIN       = "DTBegin"
OP_DATA_END         = "DTEnd"
OP_CONNECTION_END   = "CNXEnd"

class OCLTaskResult:
    def __init__(self, result):
        self.result = result

    def get_result(self):
        return self.result

class OCLTaskExecutor(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def execute(self):
        raise NotImplemented("Not implemented !")

class OCLTaskWrapper(object):
    def __init__(self, bytes_executor, loads_and_execute):
        self.bytes_executor = bytes_executor
        self.loads_and_execute = loads_and_execute

    def execute(self):
        return self.loads_and_execute(self.bytes_executor)
