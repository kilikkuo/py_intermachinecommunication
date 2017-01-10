import sys
import time
import select
import socket
import threading
from definition import OP_DATA_BEGIN, OP_DATA_END

def msg_c(a, msg):
    print("[%s] "%(str(a)) + msg)

class Server(object):
    def __init__(self, ip = "", port = 5000, max_client = 1):
        self.socket = socket.socket()
        self.socket.bind((ip, port))
        self.socket.listen(max_client)
        self.clients = {}
        self.thread = None
        self.evt_break = threading.Event()
        self.evt_break.clear()

        self.callback_for_package = None
        self.clients_temp_data = {}

    def __close_connections(self):
        try:
            while len(self.clients) > 0:
                a, c = self.clients.popitem()
                print("Closing connection [%s] ..."%(str(a)))
                c.close()
            if self.socket:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
        except:
            import traceback
            traceback.print_exc()

    def shutdown(self):
        print("[Server] Shutting down ...")
        self.__close_connections()
        if self.thread:
            self.evt_break.set()
            self.thread.join()
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
                        self.clients[addr] = client
                        read_list.append(client)
                        print("[%s] Connected !"%(str(addr)))
                    else:
                        client = None
                        for a, c in list(self.clients.items()):
                            if c is s:
                                self.__check_for_recv((a, c))
                        self.__extract_task_from_data()
                time.sleep(1)
        except:
            import traceback
            traceback.print_exc()
            print("[Exception] during server's loop for connections.")
        finally:
            self.__close_connections()

    def run_server(self, package_callback):
        assert callable(package_callback)
        print(" Run server ...")
        self.callback_for_package = package_callback

        if self.thread == None:
            self.thread = threading.Thread(target=self.__loop_for_connections)
            self.thread.daemon = True
            self.thread.start()

    def __extract_task_from_data(self):
        for a, data in list(self.clients_temp_data.items()):
            db_idx = data.find(bytearray(OP_DATA_BEGIN, "ASCII"))
            de_idx = data.find(bytearray(OP_DATA_END, "ASCII"))
            if db_idx >= 0 and de_idx >= 0:
                task = data[db_idx+7:de_idx]
                msg_c(a, str(task))
                self.callback_for_package(task)
                self.clients_temp_data[a] = b""
        pass

    def __check_for_recv(self, ac_pair):
        a, c = ac_pair
        data = c.recv(2028)
        if data and len(data):
            self.clients_temp_data[a] = self.clients_temp_data.get(a, b"") + data

if __name__ == "__main__":
    def package_callbak(package):
        print(package)
    srv = Server()
    srv.run_server(package_callbak)
    try:
        for line in sys.stdin:
            print(line)
    except:
        import traceback
        traceback.print_exc()
        print("[Exception] while lining in ")
    srv.shutdown()
