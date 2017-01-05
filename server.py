import socket

class Server():
  def __init__(self, address = ('127.0.0.1',5000), max_client=1):
      self.socket = socket.socket()
      self.socket.bind(address)
      self.socket.listen(max_client)

  def wait_for_connection(self):
      self.client, self.addr=(self.socket.accept())

srv = Server()
print("waiting for connection ...")
srv.wait_for_connection()
