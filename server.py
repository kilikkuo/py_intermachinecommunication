import time
import socket
import threading
from op_code import OP_DATA_BEGIN, OP_DATA_END

def msg_c(a, msg):
    print("[%s] "%(str(a)) + msg)

class Server():
    def __init__(self, address = ("",5000), max_client = 1):
        self.socket = socket.socket()
        self.socket.bind(address)
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
        except:
            import traceback
            traceback.print_exc()

    def shutdown(self):
        print("Shutting down ...")
        self.__close_connections()
        if self.thread:
            self.evt_break.set()
            self.thread.join()

    def run_server(self, package_callback):
        assert callable(package_callback)
        print("run_server ...")
        self.callback_for_package = package_callback
        while 1:
            try:
                client, addr = (self.socket.accept())
                print("[%s] Connected !"%(str(addr)))
                self.clients[addr] = client
                if self.thread == None:
                    self.thread = threading.Thread(target=self.__loop)
                    self.thread.daemon = True
                    self.thread.start()
                time.sleep(1)
            except:
                print("[Exception] waiting for connection >>> break")
                break
        self.shutdown()

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

    def __check_for_recv(self):
        for a, c in list(self.clients.items()):
            data = c.recv(2028)
            if data and len(data):
                self.clients_temp_data[a] = self.clients_temp_data.get(a, b"") + data

    def __loop(self):
        try:
            while 1:
                if self.evt_break.is_set():
                    break
                self.__check_for_recv()
                self.__extract_task_from_data()
                time.sleep(1)
        except:
            import traceback
            traceback.print_exc()
            print("[Exception] during server's loop.")
        finally:
            self.__close_connections()

if __name__ == "__main__":
    def package_callbak(package):
        print(package)
    srv = Server()
    srv.run_server(package_callbak)
