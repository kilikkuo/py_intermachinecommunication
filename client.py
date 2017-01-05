import socket

class Client():
   def __init__(self, address=("127.0.0.1",5000)):
      self.socket = socket.socket()
      self.socket.connect(address)

TC=Client()
