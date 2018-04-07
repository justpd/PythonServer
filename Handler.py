from Sender import *

def HandleData(socket, key, size, data):
    addr = socket.getpeername()
    print('({}) {}:{} > {}'.format(size, addr[0], addr[1], key))

    # if (key == 505001):
    #     SendData(socket, 606001, "Welcome to our server!")

