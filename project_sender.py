import os
import sys
import pickle
from definition import ResultWrapper, ExecutorWrapper, HOST_PIPE_NAME

def get_serialized_execution_wrapper():
    ba = None
    with open("program.zip", "rb") as fn:
        ba = fn.read()

    wrapper = ExecutorWrapper(ba, loader_scripts)
    serialized_executor_wrapper = pickle.dumps(wrapper)
    return serialized_executor_wrapper

def project_sender():
    if not os.path.exists(HOST_PIPE_NAME):
        os.mkfifo(HOST_PIPE_NAME)

    for line in sys.stdin:
        if "s" in line:
            pipeout = os.open(HOST_PIPE_NAME, os.O_WRONLY)
            bmsg = get_serialized_execution_wrapper()
            os.write(pipeout, bmsg)
            os.close(pipeout)

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

def extract_and_run_zip(ba):
    exec(loader_scripts)
    print(ba)
    locals()['bytes_program_loader'](ba)

ba = create_zip()
project_sender()
#
# extract_and_run_zip(ba)
