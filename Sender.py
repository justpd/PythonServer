import json

def SendData(socket, key, data):
    msg = data.encode('utf-8')
    data = key.to_bytes(4, 'little') + (len(msg)).to_bytes(4, 'little') + msg
    socket.send((len(msg) + 8).to_bytes(4, 'little'))
    socket.send(data)

    # public int roomId

    # public string opponentName
    # public int opponentRating

    # public string enemyImage
    # public int enemyImageScale

    # public string myDealerCard
    # public string oppDealerCard

    # public bool dealer

    # public string name
    # public int point
    # public int chips

def SendQuickPlaySessionInfo(socket, sessionInfo):
    print(json.dumps(sessionInfo))
    SendData(socket, 606006, json.dumps(sessionInfo))
