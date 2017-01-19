
import os
import sys
import pickle
import zipfile
import threading

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from simple_host_target.definition import send_task_to_host, sht_proxy_shutdown

def project_sender():
    try:
        print("[Sender] Enter Host & Sender's information pair ... ")
        print("[Sender] e.g. HOST.IP.1.2, 7788, Sender.IP.1.2, 9487 ")
        line = "192.168.0.14, 7788, 192.168.0.14, 9487"
        raw = ""
        # for line in sys.stdin:
        raw = line.strip().split(',')
        raw = [r.strip() for r in raw]
            # break
        assert len(raw) == 4
        ip_port_pairs = { "host_ip"     : raw[0],
                          "host_port"   : int(raw[1]),
                          "sender_ip"   : raw[2],
                          "sender_port" : int(raw[3])}
        print("[Sender] Press s + <Enter> to send a task !")
        for line in sys.stdin:
            if "s" in line:
                print("Got s, going to send ... ")
                ba = create_zip()
                send_task_to_host(ip_port_pairs, ba, loader_scripts, project_reciver)
    except:
        sht_proxy_shutdown()
        pass

def project_reciver(serialized_result):
    print("[Project_reciver] recv : %s"%(str(serialized_result)))

def create_zip():
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
    with open("./program.zip", "wb") as fn:
        fn.write(ba)

    # Extract files to execute
    with zipfile.ZipFile('./program.zip') as myzip:
        myzip.extractall('./')

    # Execution
    with open("./program.py") as f:
        code = compile(f.read(), "program.py", 'exec')
        exec(code)

    # Create results !!
    with zipfile.ZipFile('result.zip', 'w') as myzip:
        myzip.writestr('result.info', "IAMRESULT")

    result_bitstream = None
    with open("result.zip", "rb") as fn:
        result_bitstream = fn.read()
    return result_bitstream
"""
def extract_and_run_zip(ba):
    exec(loader_scripts)
    print(ba)
    locals()['bytes_program_loader'](ba)

# Exported function
def test_sample_project():
    project_sender()
    sht_proxy_shutdown()
    # To test if the zipped program can be executed correctly
    # ba = create_zip()
    # extract_and_run_zip(ba)
    pass

if __name__ == "__main__":
    test_sample_project()
