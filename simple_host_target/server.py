import os
import sys
import time
import select
import socket
import traceback
import threading

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from simple_host_target.definition import OP_DATA_BEGIN, OP_DATA_END

def msg_c(a, msg):
    print("[%s] "%(str(a)) + msg)

class Server(object):
    def __init__(self, ip = "", port = 5000, max_client = 1):
        assert (ip != "")
        self.socket = socket.socket()
        self.socket.bind((ip, port))
        self.socket.listen(max_client)
        self.clients = {}
        self.thread = threading.Thread(target=self.__loop_for_connections)
        self.thread.daemon = True
        self.evt_break = threading.Event()
        self.evt_break.clear()

        self.callback_for_package = None
        self.clients_temp_data = {}

    def __close_connections(self):
        try:
            while len(self.clients) > 0:
                c, a = self.clients.popitem()
                print("Closing connection [%s] ..."%(str(a)))
                c.close()
            if self.socket:
                self.socket.close()
        except:
            traceback.print_exc()

    def shutdown(self):
        print("[Server] Shutting down ...")
        self.__close_connections()
        if self.thread:
            self.evt_break.set()
            self.thread.join()
            self.thread = None
        print("[Server] Shutting down ... end")

    def __loop_for_connections(self):
        read_list = [self.socket]
        try:
            while 1:
                if self.evt_break.is_set():
                    break
                readable, writable, errored = select.select(read_list, [], [], 0)

                for s in readable:
                    if s is self.socket:
                        client, addr = self.socket.accept()
                        self.clients[client] = addr
                        read_list.append(client)
                        print("[%s] Connected !"%(str(addr)))
                    else:
                        client = None
                        for c, a in list(self.clients.items()):
                            if c is s:
                                self.__check_for_recv(c, a)
                            if self.__extract_task_from_data(c, a):
                                self.clients.pop(c)
                                read_list.remove(c)
                                c.close()
                                print(" REMOVED & CLOSE a socket client !!!!!!! ")

                time.sleep(1)
        except:
            traceback.print_exc()
            print("[Exception] during server's loop for connections.")
        finally:
            self.__close_connections()

    def run_server(self, package_callback):
        assert callable(package_callback)
        assert (self.thread != None)
        print(" Run server ...")
        self.callback_for_package = package_callback

        if self.thread and not self.thread.is_alive():
            self.thread.start()

    def __extract_task_from_data(self, c, a):
        data = self.clients_temp_data.get((c, a), b"")
        db_idx = data.find(bytearray(OP_DATA_BEGIN, "ASCII"))
        de_idx = data.find(bytearray(OP_DATA_END, "ASCII"))
        if db_idx >= 0 and de_idx >= 0:
            task = data[db_idx+7:de_idx]
            msg_c(a, str(task))
            self.callback_for_package(task)
            self.clients_temp_data.pop((c, a))
            return True
        return False

    def __check_for_recv(self, c, a):
        data = c.recv(2048)
        if data and len(data):
            self.clients_temp_data[(c,a)] = self.clients_temp_data.get((c,a), b"") + data

if __name__ == "__main__":
    def package_callbak(package):
        print(package)
    srv = Server()
    srv.run_server(package_callbak)
    try:
        for line in sys.stdin:
            print(line)
    except:
        traceback.print_exc()
        print("[Exception] while lining in ")
    srv.shutdown()
