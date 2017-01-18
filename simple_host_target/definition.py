OP_DATA_BEGIN       = "DTBegin"
OP_DATA_END         = "DTEnd"

HOST_PORT   = 7788
TARGET_PORT = 5566

# Exported definitions
HOST_PIPEIN_NAME = "hostpipein"
HOST_PIPEOUT_NAME = "hostpipeout"

import os
import socket
import pickle
import traceback
import threading
from simple_host_target.client import Client
from simple_host_target.generaltaskthread import TaskThread, Task

def get_local_IP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    ip = s.getsockname()[0]
    s.close()
    return ip

# Exported definitions
class ResultWrapper:
    def __init__(self, token, bytes_result):
        # To identify sender-host-target relationship
        self.token = token

        # A bytesArray which represents the serialized result.
        self.bytes_result = bytes_result

    def get_result(self):
        return self.bytes_result

# Exported definitions
class ExecutorWrapper(object):
    def __init__(self, token, bytes_program, bytes_program_loader):
        # To identify sender-host-target relationship
        self.token = token

        # A bytesArray which represents the serialized program.
        self.bytes_program = bytes_program
        # The loader to help you load the serialized program and
        # execute it !
        self.bytes_program_loader = bytes_program_loader

    def execute(self):
        exec(self.bytes_program_loader)
        data = locals()['bytes_program_loader'](self.bytes_program)
        return data

# TODO : Make token machine specific
token = 0
# TODO : Design a procedure to ensure the termination of this thread
process_thread = None

def recv_result_from_host(token, callback):
    if not os.path.exists(HOST_PIPEOUT_NAME):
        os.mkfifo(HOST_PIPEOUT_NAME)
    print("[TempTask] token(%d) going to recv_result_from_host pipeout "%(token))
    pipein = open(HOST_PIPEOUT_NAME, 'rb')
    line = pipein.read()
    if len(line) != 0:
        callback(line)
    os.unlink(HOST_PIPEOUT_NAME)

class SendTask(Task):
    def __init__(self, token, program_bitstream, program_loader_scripts, callback):
        Task.__init__(self)
        self.token = token
        self.wrapper = ExecutorWrapper(token, program_bitstream, program_loader_scripts)
        self.callback = callback

    def run(self):
        if not os.path.exists(HOST_PIPEIN_NAME):
            os.mkfifo(HOST_PIPEIN_NAME)
        print("[SendTask] token(%d) going to dump and open pipein "%(self.token))
        serialized_package = pickle.dumps(self.wrapper)
        pipeout = os.open(HOST_PIPEIN_NAME, os.O_WRONLY)
        os.write(pipeout, serialized_package)
        os.close(pipeout)
        recv_result_from_host(self.token, self.callback)

def send_task_to_host(program_bitstream, program_loader_scripts, callback):
    global process_thread
    global token
    if process_thread == None:
        process_thread = TaskThread(name="task_thread")
        process_thread.start()

    try:
        token += 1
        task = SendTask(token, program_bitstream, program_loader_scripts, callback)
        process_thread.addtask(task)
    except:
        traceback.print_exc()

def sht_proxy_shutdown():
    global process_thread
    if process_thread:
        process_thread.stop()
