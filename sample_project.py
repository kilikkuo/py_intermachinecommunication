import threading
import os
import sys
import pickle
from definition import ResultWrapper, ExecutorWrapper, HOST_PIPEIN_NAME,\
                        HOST_PIPEOUT_NAME

def get_serialized_execution_wrapper():
    ba = None
    with open("program.zip", "rb") as fn:
        ba = fn.read()

    wrapper = ExecutorWrapper(ba, loader_scripts)
    serialized_executor_wrapper = pickle.dumps(wrapper)
    return serialized_executor_wrapper

def project_sender():
    print("[Sender] Press s + <Enter> to send a task !")
    if not os.path.exists(HOST_PIPEIN_NAME):
        os.mkfifo(HOST_PIPEIN_NAME)

    try:
        recv_thread = None
        for line in sys.stdin:
            if "s" in line and recv_thread == None:
                pipeout = os.open(HOST_PIPEIN_NAME, os.O_WRONLY)
                bmsg = get_serialized_execution_wrapper()
                os.write(pipeout, bmsg)
                os.close(pipeout)
                recv_thread = threading.Thread(target=project_reciver)
                recv_thread.daemont = True
                recv_thread.start()
                recv_thread.join()
                recv_thread = None
    except:
        pass

def project_reciver():
    if not os.path.exists(HOST_PIPEOUT_NAME):
        os.mkfifo(HOST_PIPEOUT_NAME)

    pipein = open(HOST_PIPEOUT_NAME, 'rb')
    line = pipein.read()
    if len(line) != 0:
        print("[Project_reciver] recv : %s"%(str(line)))
    os.unlink(HOST_PIPEOUT_NAME)

def create_zip():
    import zipfile
    with zipfile.ZipFile('program.zip', 'w') as myzip:
        myzip.writestr('program.py', "print('I ==>> PROGRAM')")
    ba = None
    with open("program.zip", "rb") as fn:
        ba = fn.read()
    return ba

loader_scripts = """
def bytes_program_loader(ba):
    import pickle
    import zipfile

    # Convert bytes array data into zip file
    with open("../program.zip", "wb") as fn:
        fn.write(ba)

    # Extract files to execute
    with zipfile.ZipFile('../program.zip') as myzip:
        myzip.extractall('../')

    # Execution
    with open("../program.py") as f:
        code = compile(f.read(), "program.py", 'exec')
        exec(code)

    # Create results !!
    with zipfile.ZipFile('result.zip', 'w') as myzip:
        myzip.writestr('result.info', "IAMRESULT")

    ba_result = None
    with open("result.zip", "rb") as fn:
        ba_result = fn.read()
    result_wrapper = ResultWrapper(ba_result)
    serialized_result_wrapper = pickle.dumps(result_wrapper)
    return serialized_result_wrapper
"""

ba = create_zip()
project_sender()

# def extract_and_run_zip(ba):
#     exec(loader_scripts)
#     print(ba)
#     locals()['bytes_program_loader'](ba)
# To test if the zipped program can be executed correctly
# extract_and_run_zip(ba)
