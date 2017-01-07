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
        self.t = None
        self.evt_break = threading.Event()
        self.evt_break.clear()

        self.clients_temp_data = {}

    def close_connections(self):
        try:
            while len(self.clients) > 0:
                a, c = self.clients.popitem()
                c.close()
        except:
            import traceback
            traceback.print_exc()

    def shutdown(self):
        self.close_connections()
        if self.t:
            self.evt_break.set()
            self.t.join()

    def run_server(self):
        print("run_server ...")
        while 1:
            try:
                client, addr = (self.socket.accept())
                print("[%s] Connected !"%(str(addr)))
                self.clients[addr] = client
                if self.t == None:
                    self.t = threading.Thread(target=self.loop)
                    self.t.daemon = True
                    self.t.start()
                time.sleep(10)
            except:
                print(" Get exception ..... break")
                break
        self.shutdown()

    def extract_task_from_data(self):
        for a, msg in self.clients_temp_data.items():
            db_idx = msg.find(OP_DATA_BEGIN)
            de_idx = msg.find(OP_DATA_END)
            if db_idx >= 0 and de_idx >= 0:
                print (" >>>>>>>>>>>>>> GOT TASK !!")
                task_msg = msg[db_idx:de_idx+5]
                print(task_msg)
                self.clients_temp_data[a] = ""
        pass

    def check_for_recv(self):
        for a, c in self.clients.items():
            data = c.recv(20)
            msg = data.decode("UTF-8")
            if msg:
                self.clients_temp_data[a] = self.clients_temp_data.get(a, "") + msg
            print(self.clients_temp_data)
            # if data in bytearray(OP_CONNECTION_BEGIN, "UTF-8"):
            #     msg_c(a, "Start connection >>> ")
            # elif data in bytearray(OP_DATA_BEGIN, "UTF-8"):
            #     msg_c(a, "Receiving data ... start")
            # elif data in bytearray(OP_DATA_END, "UTF-8"):
            #     msg_c(a, "Receiving data ... end")
            # elif data in bytearray(OP_CONNECTION_END, "UTF-8"):
            #     msg_c(a, "Stop connection <<< ")
            #     break
            # else:
            #     msg_c(a, "Nothing is received ... ")

    def loop(self):
        try:
            while 1:
                if self.evt_break.is_set():
                    break
                self.check_for_recv()
                self.extract_task_from_data()
                time.sleep(1)
        except:
            import traceback
            traceback.print_exc()
            print("Exception: during server's loop.")
        finally:
            self.close_connections()

def start_server():
    srv = Server()
    srv.run_server()

start_server()
