from Sender import *
import base64
import json
import threading

from deuces import Card
from deuces import Deck
from deuces import Evaluator
from SqlConnect import SqlConnection


class Loby():
    def __init__(self):
        self.Clients = []
        self.Sessions = {}
        self.roomID = 0
        threading.Thread(target=self.LobbyThread).start()

    def EnterQuery(self, usersession):
        self.Clients.append(usersession)
        print(self.Clients)

    def DestroySession(self, session):
        self.Sessions.pop(session.roomID)

    # def SortByRating(self):
    #     print(self.Clients)
    #     self.Clients.sort(key=lambda x: x['rating'], reverse=True)
    #     print(self.Clients)

    def LobbyThread(self):
        while True:
            if (len(self.Clients) > 1):
                # self.SortByRating()
                session = Session(
                    self.Clients[0], self.Clients[1], self.roomID + 1)
                self.Sessions[session.roomID] = session
                self.Clients = self.Clients[2:]

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


def GetImageData(login):
    return DB.GetUserImage(login)[0]


def GetPlayerSocket(login):
    return OnlinePlayers[login]


class Session:
    def __init__(self, player_session_1, player_session_2, roomID):
        self.player_session_1 = player_session_1[0]
        self.player_session_2 = player_session_2[0]
        self.roomID = roomID

        self.chips = 500
        self.levels = [10, 20, 30, 40, 50, 60,
                       70, 80, 90, 100, 200, 300, 400, 500]
        self.point = self.levels[0]

        self.first_hand = OFCDeck()
        self.second_hand = OFCDeck()

        self.OFCDecks = {
            self.player_session_1['login']: self.first_hand,
            self.player_session_2['login']: self.second_hand
        }

        self.DefineDealer()

    def DefineDealer(self):
        self.deck = Deck()
        cards = self.deck.draw(2)

        cards_repr = Card.return_string_cards(cards).replace(
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()

        cards_repr_b = Card.return_pretty_cards(cards).replace('T', '10').replace(
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()

        print(cards_repr)
        print(cards_repr_b)
        print(cards)

        self.deck = Deck()

        if (cards[0] > cards[1]):
            print(cards_repr[:2] + ' > ' + cards_repr[-2:])
            print(self.player_session_1['login'] + ' is dealer.')
            self.dealer = self.player_session_1
            self.current = self.player_session_2
            # self.current_hand = self.GetStarterHand(self.current)
            # # self.SimulateMove(self.current_hand)
        else:
            print(cards_repr[-2:] + ' > ' + cards_repr[:2])
            print(self.player_session_2['login'] + ' is dealer.')
            self.dealer = self.player_session_2
            self.current = self.player_session_1
            # self.current_hand = self.GetStarterHand(self.current)
            # # self.SimulateMove(self.current_hand)

        imageData = GetImageData(self.current['login'])
        first_dealerCard = ''
        second_dealerCard = ''
        if (self.dealer['login'] == self.player_session_1['login']):
            first_dealerCard = cards_repr[:2].upper()
            second_dealerCard = cards_repr[-2:].upper()
        else:
            first_dealerCard = cards_repr[-2:].upper()
            second_dealerCard = cards_repr[:2].upper()

        sessioninfo = {
            'roomId': self.roomID,
            'name': 'OFC HEADSUP (500 chips)',
            'point': self.levels[0],
            'chips': self.chips,

            'dealer': True,
            'enemyImage': imageData['b64str'],
            'enemyImageScale': imageData['scale'],
            'opponentName': self.current['login'],
            'opponentRating': self.current['rating'],
            'myDealerCard': first_dealerCard,
            'oppDealerCard': second_dealerCard,
        }

        SendQuickPlaySessionInfo(GetPlayerSocket(
            self.dealer['login']), sessioninfo)

        imageData = GetImageData(self.dealer['login'])
        sessioninfo = {
            'roomId': self.roomID,
            'name': 'OFC HEADSUP (500 chips)',
            'point': self.levels[0],
            'chips': self.chips,

            'dealer': False,
            'enemyImage': imageData['b64str'],
            'enemyImageScale': imageData['scale'],
            'opponentName': self.dealer['login'],
            'opponentRating': self.dealer['rating'],
            'myDealerCard': second_dealerCard,
            'oppDealerCard': first_dealerCard,
        }

        SendQuickPlaySessionInfo(GetPlayerSocket(
            self.current['login']), sessioninfo)
        
        self.DrawNewHand(True)
    
    def DrawNewHand(self, firstHand):
        self.current_hand = self.GetStarterHand(self.current)
        sessionData = {
            'roomId': self.roomID,
            'firsthHand': firstHand,
            'hand': self.current_hand
        }
        SendQuickPlaySessionData(GetPlayerSocket(
            self.current['login']), sessionData)
        
        if (firstHand):
            SendQuickPlaySessionData(GetPlayerSocket(
                self.dealer['login']), sessionData)
        


    def SimulateMove(self, hand):
        hand = hand.split('  ')
        print(hand)
        for card in hand:
            print('Place your cards:')
            position = input(card)
            self.OFCDecks[self.current['login']].Place(card, position)

    def GetStarterHand(self, player_session):
        hand = self.deck.draw(5)

        hand_repr = Card.return_string_cards(hand).replace(
            '[', '').replace(']', '').replace(' ', '').strip()

        hand_repr_b = Card.return_pretty_cards(hand).replace('T', '10').replace(
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()

        print('{}\'s cards: {}'.format(player_session['login'], hand_repr))
        print('{}\'s cards: {}'.format(player_session['login'], hand_repr_b))

        return hand_repr

    # def __str__(self):
    #     print('Session: {} vs {} id = {}'.format(
    #         self.player_session_1['login'], self.player_session_2['login'], self.roomID))

    def SendSessionInfo(self):
        pass

class OFCDeck():
    def __init__(self):
        self.top = ['--', '--', '--']
        self.mid = ['--', '--', '--', '--', '--']
        self.bot = ['--', '--', '--', '--', '--']
        self.trunk = []

        self.hands = [self.top, self.mid, self.bot, self.trunk]

        self.top_str = ''
        self.mid_str = ''
        self.bot_str = ''

    def Place(self, card, position):
        if (len(position) == 1 and eval(position) == 3):
            self.trunk.append(Card.new(card))
        else:
            self.hands[eval(position[0])][eval(position[1])] = card

        for i in range(3):
            print(self.hands[i])
            print(len(self.hands[i]))
