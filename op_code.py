from abc import ABCMeta, abstractmethod

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
    def __init__(self, package_bytes):
        self.package_bytes = package_bytes

    @abstractmethod
    def execute(self):
        raise NotImplemented("Not implemented !")
