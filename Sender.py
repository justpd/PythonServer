import json

def SendData(socket, key, data):
    msg = data.encode('utf-8')
    data = key.to_bytes(4, 'little') + (len(msg)).to_bytes(4, 'little') + msg
    socket.send((len(msg) + 8).to_bytes(4, 'little'))
    socket.send(data)

def SendQuickPlaySessionInfo(socket, sessionInfo):
    print(json.dumps(sessionInfo))
    SendData(socket, 606006, json.dumps(sessionInfo))

def SendQuickPlaySessionData(socket, sessionData):
    print(json.dumps(sessionData))
    SendData(socket, 606007, json.dumps(sessionData))

