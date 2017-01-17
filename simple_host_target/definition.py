OP_DATA_BEGIN       = "DTBegin"
OP_DATA_END         = "DTEnd"

HOST_PORT   = 7788
TARGET_PORT = 5566

# Exported definitions
HOST_PIPEIN_NAME = "hostpipein"
HOST_PIPEOUT_NAME = "hostpipeout"

def get_local_IP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    ip = s.getsockname()[0]
    s.close()
    return ip

# Exported definitions
class ResultWrapper:
    def __init__(self, bytes_result):
        # A bytesArray which represents the serialized result.
        self.bytes_result = bytes_result

    def get_result(self):
        return self.bytes_result

# Exported definitions
class ExecutorWrapper(object):
    def __init__(self, bytes_program, bytes_program_loader):
        # A bytesArray which represents the serialized program.
        self.bytes_program = bytes_program
        # The loader to help you load the serialized program and
        # execute it !
        self.bytes_program_loader = bytes_program_loader

    def execute(self):
        exec(self.bytes_program_loader)
        data = locals()['bytes_program_loader'](self.bytes_program)
        return data
