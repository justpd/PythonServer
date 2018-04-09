from Sender import *
import base64
import json

def HandleData(socket, key, size, data):
    addr = socket.getpeername()
    print('({}) {}:{} > {}'.format(size, addr[0], addr[1], key))

    jsonData = json.loads(data)

    if (jsonData['b64str']):
        with open(jsonData['login'] + '.png', "wb") as fh:
            fh.write(base64.decodebytes(jsonData['b64str'].encode('utf-8')))

    if (key == 505001):
        SendData(socket, 606001, "Welcome to our server!")

