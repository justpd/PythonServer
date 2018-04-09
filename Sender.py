def SendData(socket, key, data):
    msg = data.encode('utf-8')
    data = key.to_bytes(4, 'little') + (len(msg)).to_bytes(4, 'little') + msg
    socket.send((len(msg) + 8).to_bytes(4, 'little'))
    socket.send(data)
