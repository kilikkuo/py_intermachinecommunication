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

from simple_host_target.definition import OP_HT_DATA_BEGIN, OP_HT_DATA_END, OP_HT_DATA_MID

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

        self.clients_temp_data = {}
        self.callbacks_info = {}

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
                # Data arrived.
                for s in readable:
                    if s is self.socket:
                        # Accept connections from client's request.
                        client, addr = self.socket.accept()
                        self.clients[client] = addr
                        read_list.append(client)
                        print("[%s] Connected !"%(str(addr)))
                    else:
                        client = None
                        for c, a in list(self.clients.items()):
                            if c is s:
                                # Collect & append data.
                                self.__check_for_recv(c, a)
                            # Analyze if data is received completely
                            if self.__extract_specific_task(c, a):
                                self.clients.pop(c)
                                read_list.remove(c)
                                c.close()
                                print(" REMOVED & CLOSE a socket client !!!!!!! ")

                time.sleep(0.01)
        except:
            traceback.print_exc()
            print("[Exception] during server's loop for connections.")
        finally:
            self.__close_connections()

    def run_server(self, callbacks_info = {}):
        # Register the callback function when specific message is received.
        # e.g.
        # { 0 : { "pre" : OP_HT_DATA_BEGIN,
        #         "post": OP_HT_DATA_END,
        #         "mid" : OP_HT_DATA_MID,
        #         "callback"  : callbak }}
        #
        # Data in between "pre" & "mid" is a repr form of ip-ports information dictionary.
        # e.g.         ip_port_pairs = { "host_ip"     : string of IP,
        #                                "host_port"   : int of PORT,
        #                                "sender_ip"   : string of IP,
        #                                "sender_port" : int of PORT}
        #
        # Data in between "mid" & "post" is a pickled bitstream.
        #
        # "callback" is going to be invoked when a *complete* message is received.
        # *complete* - enclosed by "pre" & "post"

        assert (self.thread != None)
        for v in callbacks_info.values():
            assert "pre" in v and "post" in v and "callback" in v and callable(v["callback"])
        print("Start the server ...")
        self.callbacks_info = callbacks_info

        if self.thread and not self.thread.is_alive():
            self.thread.start()

    def __extract_specific_task(self, c, a):
        # Check the completeness of received data, and callback if it's finished.
        data = self.clients_temp_data.get((c, a), b"")
        for info in self.callbacks_info.values():
            pre_idx = data.find(info["pre"])
            post_idx = data.find(info["post"])
            if pre_idx >= 0 and post_idx >= 0:
                if info.get("mid", "") and data.find(info["mid"]) >= 0:
                    mid_idx = data.find(info["mid"])
                    ipport = data[pre_idx+len(info["pre"]):mid_idx]
                    task = data[mid_idx+len(info["mid"]):post_idx]
                    info["callback"](ipport, task)
                    self.clients_temp_data.pop((c, a))
                    return True
                else:
                    task = data[pre_idx+len(info["pre"]):post_idx]
                    info["callback"](task)
                    self.clients_temp_data.pop((c, a))
                    return True
        return False

    def __check_for_recv(self, c, a):
        data = c.recv(2048)
        if data and len(data):
            self.clients_temp_data[(c,a)] = self.clients_temp_data.get((c,a), b"") + data

if __name__ == "__main__":
    def callbak(msg):
        print(msg)
    srv = Server(ip = "127.0.0.1")
    srv.run_server(callbacks_info = { 0 : { "pre" : OP_HT_DATA_BEGIN,
                                            "post": OP_HT_DATA_END,
                                            "mid" : OP_HT_DATA_MID,
                                            "callback"  : callbak }})
    try:
        for line in sys.stdin:
            print(line)
    except:
        traceback.print_exc()
        print("[Exception] while lining in ")
    srv.shutdown()
