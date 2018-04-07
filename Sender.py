def SendData(socket, key, data):
    msg = data.encode('utf-8')
    print(msg)
    print(len(msg))
    data = key.to_bytes(4, 'little') + (len(msg)).to_bytes(4, 'little') + msg
    print(data)
    socket.send(len(msg).to_bytes(4, 'little'))
    socket.send(data)
