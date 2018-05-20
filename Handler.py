from Sender import *
import base64
import json
import time
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
        threading.Thread(target=self.LobyThread).start()

    def EnterQuery(self, usersession):
        self.Clients.append(usersession)
        print(self.Clients)

    def DestroySession(self, session):
        self.Sessions.pop(session.roomID)

    def LobyThread(self):
        while True:
            if (len(self.Clients) > 1):
                # self.SortByRating()
                self.roomID += 1
                session = Session(
                    self.Clients[0], self.Clients[1], self.roomID, 500)
                self.Sessions[session.roomID] = session
                self.Clients = self.Clients[2:]

OnlinePlayers = {
    
}

DB = SqlConnection()
QuickPlayLoby = Loby()

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
    print('Requested user login : ', data)
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
    QuickPlayLoby.EnterQuery(userSession)

def QuickPlayMoveData(socket, data):
    room = QuickPlayLoby.Sessions[data['roomId']]
    if (room.fantasyHands[room.player_session_1['login']] or room.fantasyHands[room.player_session_2['login']]):
        room.FantasyMove(data['position'], data['login'])
    else:
        room.Move(data['position'])

def RequestUpdateImage(socket, data):
    print(data)
    DB.UpdateUserImage(data['login'], data['b64str'], data['scale'])
    print('Image updated')

def RequestNewRound(socket,data):
    QuickPlayLoby.Sessions[data['roomId']].SetReady(data['login'])

keys = {
    505000: RequestUserLogout,
    505001: ConfirmConnection,
    505002: RequestUserLogin,
    505003: RequestUserRegistration,
    505004: RequestUserAccountDataUpdate,
    505005: RequestEnterQuickPlay,
    505006: QuickPlayMoveData,
    505007: RequestUpdateImage,
    505010: RequestNewRound,
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
    def __init__(self, player_session_1, player_session_2, roomID, chips):
        self.player_session_1 = player_session_1[0]
        self.player_session_2 = player_session_2[0]
        self.roomID = roomID

        self.round = 0

        self.playing = False

        self.ready_players = 0

        self.chips = chips
        # TODO 10
        self.levels = [10, 20, 30, 40, 50, 60,
                       70, 80, 90, 100, 200, 300, 400, 500]
        self.lvl = 0
        self.point = self.levels[self.lvl]

        self.first_hand = OFCDeck(False)
        self.second_hand = OFCDeck(False)

        self.player_chips_1 = self.chips
        self.player_chips_2 = self.chips

        self.first_fantasy = False
        self.second_fantasy = False

        self.fantasyHands = {
            self.player_session_1['login']: self.first_fantasy,
            self.player_session_2['login']: self.second_fantasy
        }

        self.player_chips = {
            self.player_session_1['login']: self.player_chips_1,
            self.player_session_2['login']: self.player_chips_2
        }

        self.OFCDecks = {
            self.player_session_1['login']: self.first_hand,
            self.player_session_2['login']: self.second_hand
        }

        self.winner = ''

        self.DefineDealer()
    
    def SetReady(self, login):
        self.ready_players += 1
        print(self.ready_players)
        if (self.ready_players == 2):
            if (self.fantasyHands[self.current['login']] or self.fantasyHands[self.waiting['login']]):
                self.FantasyHand()
            else:
                self.NewHand()
            self.ready_players = 0
            
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

        #cheat deck
        # self.deck = Deck(
        #     'Qs,Qh,As,Ah,Td,6s,4s,3s,2s,Ts,Tc,8c,9c,Th,8h,9h,9d,9s,5h,8s,8d,5d,Kh,Ks,5c,Ac,Ad,5s,Jh,Js,4h,7c,7d,4d,6c,6d,6h,Jc,Jd,4c,3c,3d,3h,Kc,7s,7d,7c,7h,2c,2d,Kd,2h,Qc,Qd,Ac,Ad')
        self.deck = Deck()

        if (cards[0] > cards[1]):
            print(cards_repr[:2] + ' > ' + cards_repr[-2:])
            print(self.player_session_1['login'] + ' is dealer.')
            self.dealer = self.player_session_1
            self.current = self.player_session_2
            self.waiting = self.dealer
            # self.current_hand = self.GetStarterHand(self.current)
            # # self.SimulateMove(self.current_hand)
        else:
            print(cards_repr[-2:] + ' > ' + cards_repr[:2])
            print(self.player_session_2['login'] + ' is dealer.')
            self.dealer = self.player_session_2
            self.current = self.player_session_1
            self.waiting = self.dealer
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
            'name': 'OFC HEADSUP ({} chips)'.format(self.chips),
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
            'name': 'OFC HEADSUP ({} chips)'.format(self.chips),
            'point': self.levels[0],
            'chips': self.chips,

            'dealer': False,
            'enemyImage': imageData['b64str'],
            'enemyImageScale': imageData['scale'],
            'opponentName': self.waiting['login'],
            'opponentRating': self.waiting['rating'],
            'myDealerCard': second_dealerCard,
            'oppDealerCard': first_dealerCard,
        }

        SendQuickPlaySessionInfo(GetPlayerSocket(
            self.current['login']), sessioninfo)
        
        self.handIndex = 0
        self.lastPositions = ''
        self.DrawStarterHand('')
    
    def DrawStarterHand(self, opponentHand):
        if (not self.playing):
            self.current_hand = self.GetStarterHand(self.current)
            sessionData = {
                'roomId': self.roomID,
                'firstHand': True,
                'myTurn': True,
                'hand': self.current_hand,
                'position': self.lastPositions,
                'opponentHand': opponentHand,
                'myHandStr': ['', '', ''],
                'myHandRanks': [0, 0, 0],
                'oppHandStr': ['', '', ''],
                'oppHandRanks': [0, 0, 0],
            }
            sessionData['myHandStr'] = self.OFCDecks[self.current['login']].GetHandStr()
            sessionData['myHandRanks'] = self.OFCDecks[self.current['login']].GetHandRanks()
            sessionData['oppHandStr'] = self.OFCDecks[self.waiting['login']].GetHandStr()
            sessionData['oppHandRanks'] = self.OFCDecks[self.waiting['login']].GetHandRanks()
            print(self.current['login'])
            SendQuickPlaySessionData(GetPlayerSocket(
                self.current['login']), sessionData)

            sessionData['myTurn'] = False
            sessionData['myHandStr'] = self.OFCDecks[self.waiting['login']].GetHandStr()
            sessionData['myHandRanks'] = self.OFCDecks[self.waiting['login']].GetHandRanks()
            sessionData['oppHandStr'] = self.OFCDecks[self.current['login']].GetHandStr()
            sessionData['oppHandRanks'] = self.OFCDecks[self.current['login']].GetHandRanks()
            print(self.waiting['login'])
            SendQuickPlaySessionData(GetPlayerSocket(
                self.waiting['login']), sessionData)
        
            self.playing = True

    def DrawNewHand(self, opponentHand):
        self.current_hand = self.GetHand()
        sessionData = {
            'roomId': self.roomID,
            'firstHand': False,
            'myTurn': True,
            'hand': self.current_hand,
            'position': self.lastPositions,
            'opponentHand': opponentHand,
            'myHandStr': ['', '', ''],
            'myHandRanks': [0, 0, 0],
            'oppHandStr': ['', '', ''],
            'oppHandRanks': [0, 0, 0],
        }
        sessionData['myHandStr'] = self.OFCDecks[self.current['login']].GetHandStr()
        sessionData['myHandRanks'] = self.OFCDecks[self.current['login']].GetHandRanks()
        sessionData['oppHandStr'] = self.OFCDecks[self.waiting['login']].GetHandStr()
        sessionData['oppHandRanks'] = self.OFCDecks[self.waiting['login']].GetHandRanks()
        SendQuickPlaySessionData(GetPlayerSocket(
            self.current['login']), sessionData)

        sessionData['myTurn'] = False
        sessionData['myHandStr'] = self.OFCDecks[self.waiting['login']].GetHandStr()
        sessionData['myHandRanks'] = self.OFCDecks[self.waiting['login']].GetHandRanks()
        sessionData['oppHandStr'] = self.OFCDecks[self.current['login']].GetHandStr()
        sessionData['oppHandRanks'] = self.OFCDecks[self.current['login']].GetHandRanks()

        sessionData['hand'] = ''
        SendQuickPlaySessionData(GetPlayerSocket(
            self.waiting['login']), sessionData)

    def SimulateMove(self, hand):
        hand = hand.split('  ')
        print(hand)
        for card in hand:
            print('Place your cards:')
            position = input(card)
            self.OFCDecks[self.current['login']].Place(card, position)
    
    def Move(self, positions):
        print(positions)
        pos = [''.join(i) for i in grouper(positions, 2)]
        print(pos)
        hand = self.current_hand.split(',')
        i = 0
        for card in hand:
            self.OFCDecks[self.current['login']].Place(card, pos[i])
            i += 1
        
        self.lastPositions = positions
        
        self.waiting, self.current = self.current, self.waiting

        if (self.first_hand.complete and self.second_hand.complete):
            sessionData = {
                'roomId': self.roomID,
                'firstHand': False,
                'myTurn': True,
                'hand': '',
                'position': self.lastPositions,
                'opponentHand': self.current_hand,
                'myHandStr': ['', '', ''],
                'myHandRanks': [0, 0, 0],
                'oppHandStr': ['', '', ''],
                'oppHandRanks': [0, 0, 0],
            }
            sessionData['myHandStr'] = self.OFCDecks[self.current['login']].GetHandStr()
            sessionData['myHandRanks'] = self.OFCDecks[self.current['login']].GetHandRanks()
            sessionData['oppHandStr'] = self.OFCDecks[self.waiting['login']].GetHandStr()
            sessionData['oppHandRanks'] = self.OFCDecks[self.waiting['login']].GetHandRanks()
            SendQuickPlaySessionData(GetPlayerSocket(
                self.current['login']), sessionData)
            
            sessionData['opponentHand'] = ''
            sessionData['position'] = ''
            sessionData['myTurn'] = False
            sessionData['myHandStr'] = self.OFCDecks[self.waiting['login']].GetHandStr()
            sessionData['myHandRanks'] = self.OFCDecks[self.waiting['login']].GetHandRanks()
            sessionData['oppHandStr'] = self.OFCDecks[self.current['login']].GetHandStr()
            sessionData['oppHandRanks'] = self.OFCDecks[self.current['login']].GetHandRanks()
            
            SendQuickPlaySessionData(GetPlayerSocket(
                self.waiting['login']), sessionData)
            
            self.playing = False

            score = self.OFCDecks[self.current['login']].CalculateScore(self.OFCDecks[self.waiting['login']])
            self.player_chips[self.current['login']] += score * self.point
            self.player_chips[self.waiting['login']] -= score * self.point

            if (self.player_chips[self.current['login']] <= 0):
                print("Game Over : winner is " + self.waiting['login'])
                self.winner = self.waiting['login']
                if (self.waiting['login'] == self.player_session_1['login']):
                    self.player_session_1['experience'] += 5
                    self.player_session_1['gold'] += 15
                    self.player_session_1['rating'] += self.chips / 10
                    self.player_session_2['experience'] += 1
                else:
                    self.player_session_2['experience'] += 5
                    self.player_session_2['gold'] += 15
                    self.player_session_2['rating'] += self.chips / 10
                    self.player_session_1['experience'] += 1
                
                DB.UpdateUserSession(self.player_session_1)
                DB.UpdateUserSession(self.player_session_2)
                
            elif (self.player_chips[self.waiting['login']] <= 0):
                print("Game Over : winner is " + self.current['login'])
                self.winner = self.current['login']

                if (self.current['login'] == self.player_session_1['login']):
                    self.player_session_1['experience'] += 5
                    self.player_session_1['gold'] += 15
                    self.player_session_1['rating'] += self.chips / 10
                    self.player_session_2['experience'] += 1
                else:
                    self.player_session_2['experience'] += 5
                    self.player_session_2['gold'] += 15
                    self.player_session_2['rating'] += self.chips / 10
                    self.player_session_1['experience'] += 1
                
                DB.UpdateUserSession(self.player_session_1)
                DB.UpdateUserSession(self.player_session_2)

            # TODO
            # self.lvl += 1
            # self.point = self.levels[self.lvl]
            self.round += 1
            if (self.round % 2 == 0):
                self.lvl += 1
                self.point = self.levels[self.lvl]
            
            self.fantasyHands[self.current['login']] = self.OFCDecks[self.current['login']].CheckNextFantasy()
            self.fantasyHands[self.waiting['login']] = self.OFCDecks[self.waiting['login']].CheckNextFantasy()

            quickPlaySessionNewRound = {
                'roomId': self.roomID,
                'dealer': True,
                'myScore': score,
                'point': self.point,
                'winner': self.winner,
                'myBroken': self.OFCDecks[self.current['login']].dead,
                'oppBroken': self.OFCDecks[self.waiting['login']].dead,
                'myFantasy': self.fantasyHands[self.current['login']],
                'oppFantasy': self.fantasyHands[self.waiting['login']],
                'hand': '',
                'oppHandStr': ''
            }

            print(self.current['login'])
            SendQuickPlaySessionNewRound(GetPlayerSocket(
                self.current['login']), quickPlaySessionNewRound)

            print(self.waiting['login'])
            quickPlaySessionNewRound['dealer'] = False
            quickPlaySessionNewRound['myScore'] *= -1
            quickPlaySessionNewRound['myBroken'], quickPlaySessionNewRound['oppBroken'] = quickPlaySessionNewRound['oppBroken'], quickPlaySessionNewRound['myBroken']
            quickPlaySessionNewRound['myFantasy'], quickPlaySessionNewRound['oppFantasy'] = quickPlaySessionNewRound['oppFantasy'], quickPlaySessionNewRound['myFantasy']
            SendQuickPlaySessionNewRound(GetPlayerSocket(
                self.waiting['login']), quickPlaySessionNewRound)
            
            if (self.winner != ''):
                QuickPlayLoby.DestroySession(self)
            
        else:
            self.handIndex += 1

            if (self.handIndex > 1):
                self.DrawNewHand(self.current_hand)
            else:
                self.DrawStarterHand(self.current_hand)

    def NewHand(self):
        self.deck = Deck()
        self.first_hand = OFCDeck(False)
        self.second_hand = OFCDeck(False)
        self.OFCDecks = {
            self.player_session_1['login']: self.first_hand,
            self.player_session_2['login']: self.second_hand
        }
        self.handIndex = 0
        self.lastPositions = ''
        self.current_hand = ''
        self.dealer = self.current
        self.current, self.waiting = self.waiting, self.current
        time.sleep(5)
        self.DrawStarterHand('')
    
    def FantasyHand(self):
        self.deck = Deck()
        self.first_hand = OFCDeck(self.fantasyHands[self.player_session_1['login']])
        self.second_hand = OFCDeck(self.fantasyHands[self.player_session_2['login']])
        self.OFCDecks = {
            self.player_session_1['login']: self.first_hand,
            self.player_session_2['login']: self.second_hand
        }
        self.handIndex = 0
        self.lastPositions = ''
        self.current_hand = ''
        self.current, self.waiting = self.waiting, self.current

        time.sleep(5)

        self.current_hands = {
            self.player_session_1['login']: '',
            self.player_session_2['login']: ''
        }
        self.looser = False

        if (self.fantasyHands[self.player_session_1['login']] and not self.playing):
            self.DrawFantasyHand(self.player_session_1['login'])
        elif (not self.playing):
            self.looser = self.player_session_1
        else:
            print('BUG')
        
        if (self.fantasyHands[self.player_session_2['login']] and not self.playing):
            self.DrawFantasyHand(self.player_session_2['login'])
        elif (not self.playing):
            self.looser = self.player_session_2
        else:
            print('BUG')
        
        print('Looser: ', self.looser)

        if (self.looser and not self.playing):
            self.current_hands[self.looser['login']] = self.GetStarterHand(self.looser)
            sessionData = {
                'roomId': self.roomID,
                'firstHand': True,
                'myTurn': True,
                'hand': self.current_hands[self.looser['login']],
                'position': '',
                'opponentHand': '',
                'myHandStr': ['', '', ''],
                'myHandRanks': [0, 0, 0],
                'oppHandStr': ['', '', ''],
                'oppHandRanks': [0, 0, 0],
            }
            sessionData['myHandStr'] = self.OFCDecks[self.looser['login']].GetHandStr()
            sessionData['myHandRanks'] = self.OFCDecks[self.looser['login']].GetHandRanks()
            print('Sending to :' + self.looser['login'])
            SendQuickPlaySessionData(GetPlayerSocket(
                self.looser['login']), sessionData)
        time.sleep(5)
    
    def FantasyMove(self, positions, login):
        print(positions)
        pos = [''.join(i) for i in grouper(positions, 2)]
        print(pos)
        hand = self.current_hands[login].split(',')
        i = 0
        for card in hand:
            self.OFCDecks[login].Place(card, pos[i])
            i += 1

        if (self.looser and login == self.looser['login']):
            print('Looser moved.')
            if (self.OFCDecks[login].complete):
                sessionData = {
                    'roomId': self.roomID,
                    'firstHand': False,
                    'myTurn': False,
                    'hand': '',
                    'position': '',
                    'opponentHand': '',
                    'myHandStr': ['', '', ''],
                    'myHandRanks': [0, 0, 0],
                    'oppHandStr': ['', '', ''],
                    'oppHandRanks': [0, 0, 0],
                }
                sessionData['myHandStr'] = self.OFCDecks[login].GetHandStr()
                sessionData['myHandRanks'] = self.OFCDecks[login].GetHandRanks()
                SendQuickPlaySessionData(GetPlayerSocket(login), sessionData)
            else:
                self.current_hands[login] = self.GetHand()
                sessionData = {
                    'roomId': self.roomID,
                    'firstHand': False,
                    'myTurn': True,
                    'hand': self.current_hands[login],
                    'position': '',
                    'opponentHand': '',
                    'myHandStr': ['', '', ''],
                    'myHandRanks': [0, 0, 0],
                    'oppHandStr': ['', '', ''],
                    'oppHandRanks': [0, 0, 0],
                }
                sessionData['myHandStr'] = self.OFCDecks[login].GetHandStr()
                sessionData['myHandRanks'] = self.OFCDecks[login].GetHandRanks()
                SendQuickPlaySessionData(GetPlayerSocket(login), sessionData)
        else:
            sessionData = {
                'roomId': self.roomID,
                'firstHand': False,
                'myTurn': False,
                'hand': '',
                'position': '',
                'opponentHand': '',
                'myHandStr': ['', '', ''],
                'myHandRanks': [0, 0, 0],
                'oppHandStr': ['', '', ''],
                'oppHandRanks': [0, 0, 0],
            }
            sessionData['myHandStr'] = self.OFCDecks[login].GetHandStr()
            sessionData['myHandRanks'] = self.OFCDecks[login].GetHandRanks()
            SendQuickPlaySessionData(GetPlayerSocket(login), sessionData)
        
        if (self.first_hand.complete and self.second_hand.complete):
            score = self.OFCDecks[self.player_session_1['login']].CalculateScore(
                self.OFCDecks[self.player_session_2['login']])
            
            self.player_chips[self.player_session_1['login']] += score * self.point
            self.player_chips[self.player_session_2['login']] -= score * self.point

            self.playing = False

            if (self.player_chips[self.player_session_1['login']] <= 0):
                print("Game Over : winner is " + self.player_session_2['login'])
                self.winner = self.player_session_2['login']

                self.player_session_2['experience'] += 5
                self.player_session_2['gold'] += 15
                self.player_session_2['rating'] += self.chips / 10
                self.player_session_1['experience'] += 30

                DB.UpdateUserSession(self.player_session_1)
                DB.UpdateUserSession(self.player_session_2)
            elif (self.player_chips[self.player_session_2['login']] <= 0):
                print("Game Over : winner is " + self.player_session_1['login'])
                self.winner = self.player_session_1['login']

                self.player_session_1['experience'] += 5
                self.player_session_1['gold'] += 15
                self.player_session_1['rating'] += self.chips / 10
                self.player_session_2['experience'] += 1

                DB.UpdateUserSession(self.player_session_1)
                DB.UpdateUserSession(self.player_session_2)

            self.fantasyHands[self.player_session_1['login']
                              ] = self.OFCDecks[self.player_session_1['login']].CheckNextFantasy()
            self.fantasyHands[self.player_session_2['login']
                              ] = self.OFCDecks[self.player_session_2['login']].CheckNextFantasy()

            quickPlaySessionNewRound = {
                'roomId': self.roomID,
                'dealer': True,
                'myScore': score,
                'point': self.point,
                'winner': self.winner,
                'myBroken': self.OFCDecks[self.player_session_1['login']].dead,
                'oppBroken': self.OFCDecks[self.player_session_2['login']].dead,
                'myFantasy': self.fantasyHands[self.player_session_1['login']],
                'oppFantasy': self.fantasyHands[self.player_session_2['login']],
                'hand': '',
                'oppHandStr': ''
            }

            print(self.player_session_1['login'])
            quickPlaySessionNewRound['oppHandStr'] = self.OFCDecks[self.player_session_2['login']].GetHandStr()
            quickPlaySessionNewRound['hand'] = self.OFCDecks[self.player_session_2['login']].GetStringDeck()
            SendQuickPlaySessionNewRound(GetPlayerSocket(
                self.player_session_1['login']), quickPlaySessionNewRound)

            print(self.player_session_2['login'])
            quickPlaySessionNewRound['oppHandStr'] = self.OFCDecks[self.player_session_1['login']].GetHandStr()
            quickPlaySessionNewRound['hand'] = self.OFCDecks[self.player_session_1['login']].GetStringDeck()
            quickPlaySessionNewRound['dealer'] = False
            quickPlaySessionNewRound['myScore'] *= -1
            quickPlaySessionNewRound['myBroken'], quickPlaySessionNewRound[
                'oppBroken'] = quickPlaySessionNewRound['oppBroken'], quickPlaySessionNewRound['myBroken']
            quickPlaySessionNewRound['myFantasy'], quickPlaySessionNewRound[
                'oppFantasy'] = quickPlaySessionNewRound['oppFantasy'], quickPlaySessionNewRound['myFantasy']
            SendQuickPlaySessionNewRound(GetPlayerSocket(
                self.player_session_2['login']), quickPlaySessionNewRound)

            if (self.winner != ''):
                QuickPlayLoby.DestroySession(self)

    def DrawFantasyHand(self, login):
        if (not self.playing):
            print('Drawing fantasy hand for: ' + login)
            self.current_hands[login] = self.GetFantasyHand(login)
            sessionData = {
                'roomId': self.roomID,
                'firstHand': True,
                'myTurn': True,
                'hand': self.current_hands[login],
                'position': '',
                'opponentHand': '',
                'myHandStr': ['','',''],
                'myHandRanks': [0, 0, 0],
                'oppHandStr': ['', '', ''],
                'oppHandRanks': [0, 0, 0],
            }
            SendQuickPlaySessionData(GetPlayerSocket(login), sessionData)
            self.playing = True

    def GetStarterHand(self, player_session):
        hand = self.deck.draw(5)

        hand_repr = Card.return_string_cards(hand).replace(
            '[', '').replace(']', '').replace(' ', '').strip()

        hand_repr_b = Card.return_pretty_cards(hand).replace('T', '10').replace(
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()

        print('{}\'s cards: {}'.format(player_session['login'], hand_repr))
        print('{}\'s cards: {}'.format(player_session['login'], hand_repr_b))

        return hand_repr
    
    def GetHand(self):
        hand = self.deck.draw(3)

        hand_repr = Card.return_string_cards(hand).replace(
            '[', '').replace(']', '').replace(' ', '').strip()

        hand_repr_b = Card.return_pretty_cards(hand).replace('T', '10').replace(
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()

        print('{}\'s cards: {}'.format(self.current['login'], hand_repr))
        print('{}\'s cards: {}'.format(self.current['login'], hand_repr_b))

        return hand_repr

    def GetFantasyHand(self, login):
        hand = self.deck.draw(14)

        hand_repr = Card.return_string_cards(hand).replace(
            '[', '').replace(']', '').replace(' ', '').strip()

        hand_repr_b = Card.return_pretty_cards(hand).replace('T', '10').replace(
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()

        print('{}\'s cards: {}'.format(login, hand_repr))
        print('{}\'s cards: {}'.format(login, hand_repr_b))

        return hand_repr

class OFCDeck():
    def __init__(self, fantasy):
        self.top = ['--', '--', '--']
        self.mid = ['--', '--', '--', '--', '--']
        self.bot = ['--', '--', '--', '--', '--']
        self.trunk = []
        self.complete = False

        self.hands = [self.top, self.mid, self.bot, self.trunk]

        self.top_str = ''
        self.top_score = 0
        self.top_rank = 0
        self.mid_str = ''
        self.mid_rank = 0
        self.mid_score = 0
        self.bot_str = ''
        self.bot_score = 0
        self.bot_rank = 0

        self.dead = False

        self.fantasy = fantasy

        self.evaluator = Evaluator()
    
    def GetStringDeck(self):
        return ','.join(self.hands[0]) + ',' + ','.join(self.hands[1]) + ',' + ','.join(self.hands[2])
    
    def CheckNextFantasy(self):
        if (self.dead):
            return False
        else:
            if (self.fantasy):
                if (self.top_rank <= 2467 or self.bot_rank <= 166):
                    return True
                else:
                    return False
            else:
                if (self.top_rank <= 3985):
                    return True
                else:
                    return False

    def CalculateScore(self, opponentDeck):
        score = 0
        if (self.dead):
            self.top_score = 0
            self.mid_score = 0
            self.bot_score = 0
            if (opponentDeck.dead):
                return 0
            else:
                score -= 6    
                score -= opponentDeck.top_score
                score -= opponentDeck.mid_score
                score -= opponentDeck.bot_score
                return score
        else:
            if (opponentDeck.dead):
                score = self.top_score + self.mid_score + self.bot_score + 6
                return score
            else:
                score = self.top_score + self.mid_score + self.bot_score - \
                    opponentDeck.top_score - opponentDeck.mid_score - opponentDeck.bot_score
                if (self.top_rank < opponentDeck.top_rank):
                    score += 1
                else:
                    score -= 1

                if (self.mid_rank < opponentDeck.mid_rank):
                    score += 1
                else:
                    score -= 1

                if (self.bot_rank < opponentDeck.bot_rank):
                    score += 1
                else:
                    score -= 1

                return score

    def Place(self, card, position):
        print('Placing: '+ card + ' at ' + position)
        if (eval(position[0]) == 3):
            self.trunk.append(Card.new(card))
        else:
            self.hands[eval(position[0])][eval(position[1])] = card

        for i in range(4):
            print(self.hands[i])
        
        if (self.top_rank == 0):
            self.top_str, self.top_rank = self.CheckHand(self.top)
            self.top_str = self.CheckCombination(self.top_str, self.top_rank, self.top, 0)
            
        if (self.mid_rank == 0):
            self.mid_str, self.mid_rank = self.CheckHand(self.mid)
            self.mid_str = self.CheckCombination(self.mid_str, self.mid_rank, self.mid, 1)

        if (self.bot_rank == 0):
            self.bot_str, self.bot_rank = self.CheckHand(self.bot)
            self.bot_str = self.CheckCombination(self.bot_str, self.bot_rank, self.bot, 2)

        if (self.top_rank > 0 and self.mid_rank > 0 and self.bot_rank > 0):
            self.complete = True
        
            if (self.top_rank >= self.mid_rank and self.mid_rank >= self.bot_rank):
                self.dead = False
            else:
                self.dead = True
    
    def GetHandStr(self):
        return [self.top_str,self.mid_str,self.bot_str]

    def GetHandRanks(self):
        return [self.top_rank, self.mid_rank, self.bot_rank]
    
    def CheckCombination(self, hand, rank, hand_values, hand_index):
        if (hand == 'High Card'):
            hand = self.CheckHighCard(hand, rank)
        elif (hand == 'Pair'):
            hand = self.CheckPair(hand, rank, hand_index)
        elif (hand == 'Two Pair'):
            hand = self.CheckTwoPairs(hand, hand_values)
        elif (hand == 'Three of a Kind'):
            hand = self.CheckThree(hand, rank, hand_index)
            if (hand_index == 1):
                hand += '2'
                self.mid_score = 2
        elif (hand == 'Straight'):
            hand = self.CheckStraight(hand, hand_values)
            if (hand_index == 1):
                hand += '4'
                self.mid_score = 4
            elif (hand_index == 2):
                hand += '2'
                self.bot_score = 2
        elif (hand == 'Flush'):
            hand = self.CheckFlush(hand, hand_values)
            if (hand_index == 1):
                hand += '8'
                self.mid_score = 8
            elif (hand_index == 2):
                hand += '4'
                self.bot_score = 4
        elif (hand == 'Full House'):
            hand = self.CheckHouse(hand, hand_values)
            if (hand_index == 1):
                hand += '12'
                self.mid_score = 12
            elif (hand_index == 2):
                hand += '6'
                self.bot_score = 6
        elif (hand == 'Four of a Kind'):
            hand = self.CheckFour(hand, rank)
            if (hand_index == 1):
                hand += '20'
                self.mid_score = 20
            elif (hand_index == 2):
                hand += '10'
                self.bot_score = 10
        elif (hand == 'Straight Flush'):
            if (rank > 1):
                hand = self.CheckStraight(hand, hand_values)
                if (hand_index == 1):
                    hand += '30'
                    self.mid_score = 30
                elif (hand_index == 2):
                    hand += '15'
                    self.bot_score = 15
            else:
                hand = 'Royal Flush.'
                if (hand_index == 1):
                    hand += '50'
                    self.mid_score = 50
                elif (hand_index == 2):
                    hand += '25'
                    self.bot_score = 25

        
        return hand
    
    def CheckTwoPairs(self, hand, hand_values):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        names = ['Deuces', 'Threes', 'Fours', 'Fives', 'Sixes', 'Sevens', 'Eights','Nines','Tens','Jacks','Queens','Kings','Aces']
        hand_values_uniq = list(set(hand_values[0][0] + hand_values[1][0] + \
            hand_values[2][0] + hand_values[3][0] + hand_values[4][0]))
        
        hand_values = hand_values[0][0] + hand_values[1][0] + hand_values[2][0] + hand_values[3][0] + hand_values[4][0]

        pares = []

        for value in hand_values_uniq:
            if (hand_values.count(value) == 2):
                pares.append(value)
        
        pares.sort()
        hand += ' ' + names[values.index(pares[0])]
        hand += ' And ' + names[values.index(pares[1])] + '.'

        return hand

    def CheckHouse(self, hand, hand_values):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        names = ['Deuces', 'Threes', 'Fours', 'Fives', 'Sixes', 'Sevens', 'Eights','Nines','Tens','Jacks','Queens','Kings','Aces']
        hand_values_uniq = list(set(hand_values[0][0] + hand_values[1][0] + \
            hand_values[2][0] + hand_values[3][0] + hand_values[4][0]))
        
        hand_values = hand_values[0][0] + hand_values[1][0] + hand_values[2][0] + hand_values[3][0] + hand_values[4][0]

        for value in hand_values_uniq:
            if (hand_values.count(value) == 2):
                hand += ' ' + names[values.index(value)]
                break
        for value in hand_values_uniq:
            if (hand_values.count(value) == 3):
                hand += ' Full of ' + names[values.index(value)] + '.'
        
        return hand

    def CheckFour(self, hand, rank):
        if (rank > 154):
            hand += ' Deuces.'
        elif (rank > 142):
            hand += ' Threes.'
        elif (rank > 130):
            hand += ' Fours.'
        elif (rank > 118):
            hand += ' Fives.'
        elif (rank > 106):
            hand += ' Sixes.'
        elif (rank > 94):
            hand += ' Sevens.'
        elif (rank > 82):
            hand += ' Eights.'
        elif (rank > 70):
            hand += ' Nines.'
        elif (rank > 58):
            hand += ' Tens.'
        elif (rank > 46):
            hand += ' Jacks.'
        elif (rank > 34):
            hand += ' Queens.'
        elif (rank > 22):
            hand += ' Kings.'
        else:
            hand += ' Aces.'

        return hand
    
    def CheckFlush(self, hand, hand_values):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        hand_values = hand_values[0][0] + hand_values[1][0] + \
            hand_values[2][0] + hand_values[3][0] + hand_values[4][0]
        for value in values[::-1]:
            if value in hand_values:
                if value == 'A':
                    hand += ' Ace High.'
                elif value == 'K':
                    hand += ' King High.'
                elif value == 'Q':
                    hand += ' Queen High.'
                elif value == 'J':
                    hand += ' Jack High.'
                elif value == 'T':
                    hand += ' Ten High.'
                elif value == '9':
                    hand += ' Nine High.'
                elif value == '8':
                    hand += ' Eight High.'
                elif value == '7':
                    hand += ' Seven High.'
                break
        return hand

    def CheckStraight(self, hand, hand_values):
        values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        hand_values = hand_values[0][0] + hand_values[1][0] + hand_values[2][0] + hand_values[3][0] + hand_values[4][0]
        for value in values[::-1]:
            if value in hand_values:
                if value == 'A':
                    if ('K' in hand_values):
                        hand += ' Ten to Ace.'
                    else:
                        hand += ' Ace to Five.'
                elif value == 'K':
                    hand += ' Nine to King.'
                elif value == 'Q':
                    hand += ' Eight to Queen.'
                elif value == 'J':
                    hand += ' Seven to Jack.'
                elif value == 'T':
                    hand += ' Six to Ten.'
                elif value == '9':
                    hand += ' Five to Nine.'
                elif value == '8':
                    hand += ' Four to Eight.'
                elif value == '7':
                    hand += ' Three to Seven.'
                elif value == '6':
                    hand += ' Two to Six.'
                break
        return hand

    def CheckHighCard(self, hand, rank):
        if (rank > 7458):
            hand += ' Seven.'
        elif (rank > 7444):
            hand += ' Eight.'
        elif (rank > 7410):
            hand += ' Nine.'
        elif (rank > 7341):
            hand += ' Ten.'
        elif (rank > 7216):
            hand += ' Jack.'
        elif (rank > 7007):
            hand += ' Queen.'
        elif (rank > 6678):
            hand += ' King.'
        else:
            hand += ' Ace.'

        return hand

    def CheckPair(self, hand, rank, index):
        if (rank > 5965):
            hand += ' of Deuces.'
        elif (rank > 5745):
            hand += ' of Threes.'
        elif (rank > 5525):
            hand += ' of Fours.'
        elif (rank > 5305):
            hand += ' of Fives.'
        elif (rank > 5085):
            hand += ' of Sixes.'
            if (index == 0):
                hand += '1'
                self.top_score = 1 
        elif (rank > 4865):
            hand += ' of Sevens.'
            if (index == 0):
                hand += '2'
                self.top_score = 2 
        elif (rank > 4645):
            hand += ' of Eights.'
            if (index == 0):
                hand += '3'
                self.top_score = 3 
        elif (rank > 4425):
            hand += ' of Nines.'
            if (index == 0):
                hand += '4'
                self.top_score = 4 
        elif (rank > 4205):
            hand += ' of Tens.'
            if (index == 0):
                hand += '5'
                self.top_score = 5 
        elif (rank > 3985):
            hand += ' of Jacks.'
            if (index == 0):
                hand += '6'
                self.top_score = 6 
        elif (rank > 3765):
            hand += ' of Queens.'
            if (index == 0):
                hand += '7'
                self.top_score = 7 
        elif (rank > 3545):
            hand += ' of Kings.'
            if (index == 0):
                hand += '8'
                self.top_score = 8 
        else:
            hand += ' of Aces.'
            if (index == 0):
                hand += '9'
                self.top_score = 9 
        
        return hand
    
    def CheckThree(self, hand, rank, index):
        if (rank > 2401):
            hand += ' Deuces.'
            if (index == 0):
                hand += '10'
                self.top_score = 10 
        elif (rank > 2335):
            hand += ' Threes.'
            if (index == 0):
                hand += '11'
                self.top_score = 11 
        elif (rank > 2269):
            hand += ' Fours.'
            if (index == 0):
                hand += '12'
                self.top_score = 12 
        elif (rank > 2203):
            hand += ' Fives.'
            if (index == 0):
                hand += '13'
                self.top_score = 13 
        elif (rank > 2137):
            hand += ' Sixes.'
            if (index == 0):
                hand += '14'
                self.top_score = 14 
        elif (rank > 2071):
            hand += ' Sevens.'
            if (index == 0):
                hand += '15'
                self.top_score = 15 
        elif (rank > 2005):
            hand += ' Eights.'
            if (index == 0):
                hand += '16'
                self.top_score = 16 
        elif (rank > 1939):
            hand += ' Nines.'
            if (index == 0):
                hand += '17'
                self.top_score = 17 
        elif (rank > 1873):
            hand += ' Tens.'
            if (index == 0):
                hand += '18'
                self.top_score = 18 
        elif (rank > 1807):
            hand += ' Jacks.'
            if (index == 0):
                hand += '19'
                self.top_score = 19 
        elif (rank > 1741):
            hand += ' Queens.'
            if (index == 0):
                hand += '20'
                self.top_score = 20 
        elif (rank > 1675):
            hand += ' Kings.'
            if (index == 0):
                hand += '21'
                self.top_score = 21 
        else:
            hand += ' Aces.'
            if (index == 0):
                hand += '22'
                self.top_score = 22 
        
        return hand

    def CheckHand(self, hand):
        blank = 0
        for card in hand:
            if (card == '--'):
                blank += 1
        if (blank == 0):
            print('Found combination.')
            combination = []
            for card in hand:
                combination.append(Card.new(card))
            if (len(combination) == 3):
                return self.evaluate_three(combination)
            else:
                hand_score = self.evaluator._five(combination)
                hand_class = self.evaluator.class_to_string(
                    self.evaluator.get_rank_class(hand_score))

                print(hand_class)
                print(hand_score)
                
                return hand_class, hand_score
        else:
            return '', 0
        
    def evaluate_three(self, hand):
        _VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

        values = []
        for card in hand:
            card = Card.int_to_str(card).upper().replace(
                ' ', '').replace('[', '').replace(']', '')
            if (card[0] not in values):
                values.append(card[0])

        print(values)
        print([item for item in _VALUES if item not in values])
        values = [item for item in _VALUES if item not in values]
        i = 0
        j = 1

        hand.append(Card.new(values[i] + 's'))
        hand.append(Card.new(values[j] + 'c'))

        hand_score = self.evaluator._three(hand)
        hand_class = self.evaluator.class_to_string(
            self.evaluator.get_rank_class(hand_score))

        if (hand_class == 'Straight'):
            print('Получили стрит, меняем карты...')
            j += 1
            hand[3] = Card.new(values[i] + 's')
            hand[4] = Card.new(values[j] + 'c')

            hand_score = self.evaluator._three(hand)
            hand_class = self.evaluator.class_to_string(
                self.evaluator.get_rank_class(hand_score))

        return hand_class, hand_score

def grouper(iterable, n):
    args = [iter(iterable)] * n
    return zip(*args)
