from Sender import *
import base64
import json
from SqlConnect import SqlConnection
from QuickPlaySession import Loby

OnlinePlayers = {
    
}

DB = SqlConnection()
QuickPlayLobby = Loby()

        # S_ConfirmConnection = 606001,
        # S_ConfirmUserLogin = 606002,
        # S_AbortUserLogin = 606003,
        # S_ConfirmUserRegistration = 606004,
        # S_AbortUserRegistration = 606005,
        # S_SendQuickPlaySessionInfo = 606006,
        # S_SendQuickPlaySessionData = 606007,
        # S_UpdateUserSessionData = 606008,
        # S_UpdateUserImage = 606009

        # C_RequestUserLogout = 505000,
        # C_ConfirmConnection = 505001,
        # C_RequestUserLogin = 505002,
        # C_RequestUserRegistration = 505003,
        # C_RequestUserAccountDataUpdate = 505004,
        # C_RequestEnterQuickPlay = 505005,
        # C_QuickPlayMoveData = 505006,
        # C_RequestUpdateImage = 505007

def ConfirmConnection(socket, jsonData):
    SendData(socket, 606001, "Welcome to our server!")


def RequestUserRegistration(socket, data):
    # DB.registerUser()
    print(data)
    if (DB.registerUser(data['login'], data['password'], data['email'])):
        print(data['login'] + ' joined us!')
        SendData(socket, 606004, "Succesfully registered.")
        DB.SetDefaultUserImage(data['login'])
    else:
        SendData(socket, 606005, "Registration error.")


def RequestUserLogin(socket, data):
    print(data)
    if (DB.loginUser(data['login'], data['password'])):
        userSession = DB.InitialazeUserSession(data['login'])
        print(data['login'] + ' logged in.')
        try:
            OnlinePlayers[data['login']]
        except:
            OnlinePlayers[data['login']] = socket

        SendData(socket, 606002, json.dumps(userSession)[1:-1])
        SendData(socket, 606009, json.dumps(
            DB.GetUserImage(data['login']))[1:-1])

    else:
        print('Login aborted.')
        SendData(socket, 606003, "Error.")


def RequestUserAccountDataUpdate(socket, data):
    print(data)
    userSession = DB.InitialazeUserSession(data['login'])
    SendData(socket, 606008, json.dumps(userSession)[1:-1])
    SendData(socket, 606009, json.dumps(DB.GetUserImage(data['login']))[1:-1])

        # private static void Handle_UserLogout(int index, byte[] data)
        # {
        #     PacketBuffer buffer = new PacketBuffer()
        #     buffer.WriteBytes(data)
        #     int packetNum = buffer.ReadInteger()
        #     string msg = buffer.ReadString()
        #     buffer.Dispose()

        #     Console.WriteLine(msg + "logged out.")
        #     ServerTCP.OnlineClients.Remove(msg)
        # }


def RequestUserLogout(socket, data):
    print(data['login'] + ' gone offline.')
    OnlinePlayers.pop(data['login'])

def RequestEnterQuickPlay(socket, data):
    print(data['login'] + 'requested to enter quick play.')
    userSession = DB.InitialazeUserSession(data['login'])
    QuickPlayLobby.EnterQuery(userSession)


def QuickPlayMoveData(socket, data):
    pass

def RequestUpdateImage(socket, data):
    print(data)
    DB.UpdateUserImage(data['login'], data['b64str'], data['scale'])
    print('Image updated')


keys = {
    505000: RequestUserLogout,
    505001: ConfirmConnection,
    505002: RequestUserLogin,
    505003: RequestUserRegistration,
    505004: RequestUserAccountDataUpdate,
    505005: RequestEnterQuickPlay,
    505006: QuickPlayMoveData,
    505007: RequestUpdateImage,

}


def HandleData(socket, key, size, data):
    addr = socket.getpeername()
    print('({}) {}:{} > {}'.format(size, addr[0], addr[1], key))

    jsonData = json.loads(data)

    # if (jsonData['b64str']):
    #     with open(jsonData['login'] + '.png', "wb") as fh:
    #         fh.write(base64.decodebytes(jsonData['b64str'].encode('utf-8')))

    if (key in keys.keys()):
        keys[key](socket, jsonData)
    else:
        print(key)

def DisconnectUser(socket):
    for k, v in OnlinePlayers.items():
        if (v == socket):
            RequestUserLogout(socket, {'login': k})
            break
