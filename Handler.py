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
                self.roomID += 1
                session = Session(
                    self.Clients[0], self.Clients[1], self.roomID)
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
    QuickPlayLobby.Sessions[data['roomId']].Move(data['position'])

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
        self.current_hand = self.GetStarterHand(self.current)
        sessionData = {
            'roomId': self.roomID,
            'firstHand': True,
            'myTurn': True,
            'hand': self.current_hand,
            'position': self.lastPositions,
            'opponentHand': opponentHand,
            'myHandStr': '',
            'myHandRanks': '',
            'oppHandStr': '',
            'oppHandRanks': '',
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

        SendQuickPlaySessionData(GetPlayerSocket(
            self.waiting['login']), sessionData)

    def DrawNewHand(self, opponentHand):
        self.current_hand = self.GetHand()
        sessionData = {
            'roomId': self.roomID,
            'firstHand': False,
            'myTurn': True,
            'hand': self.current_hand,
            'position': self.lastPositions,
            'opponentHand': opponentHand,
            'myHandStr': '',
            'myHandRanks': '',
            'oppHandStr': '',
            'oppHandRanks': '',
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
                'myHandStr': '',
                'myHandRanks': '',
                'oppHandStr': '',
                'oppHandRanks': '',
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
            
        else:
            self.handIndex += 1

            if (self.handIndex > 1):
                self.DrawNewHand(self.current_hand)
            else:
                self.DrawStarterHand(self.current_hand)


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
        self.complete = False

        self.hands = [self.top, self.mid, self.bot, self.trunk]

        self.top_str = ''
        self.top_rank = 0
        self.mid_str = ''
        self.mid_rank = 0
        self.bot_str = ''
        self.bot_rank = 0

        self.evaluator = Evaluator()

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
            self.top_str = self.CheckCombination(self.top_str, self.top_rank, self.top)
            
        if (self.mid_rank == 0):
            self.mid_str, self.mid_rank = self.CheckHand(self.mid)
            self.mid_str = self.CheckCombination(self.mid_str, self.mid_rank, self.mid)

        if (self.bot_rank == 0):
            self.bot_str, self.bot_rank = self.CheckHand(self.bot)
            self.bot_str = self.CheckCombination(self.bot_str, self.bot_rank, self.bot)

        if (self.top_rank > 0 and self.mid_rank > 0 and self.bot_rank > 0):
            self.complete = True
    
    def GetHandStr(self):
        return [self.top_str,self.mid_str,self.bot_str]

    def GetHandRanks(self):
        return [self.top_rank, self.mid_rank, self.bot_rank]
    
    def CheckCombination(self, hand, rank, hand_values):
        if (hand == 'High Card'):
            hand = self.CheckHighCard(hand, rank)
        elif (hand == 'Pair'):
            hand = self.CheckPair(hand, rank)
        elif (hand == 'Two Pair'):
            hand = self.CheckTwoPairs(hand, hand_values)
        elif (hand == 'Three of a Kind'):
            hand = self.CheckThree(hand, rank)
        elif (hand == 'Straight'):
            hand = self.CheckStraight(hand, hand_values)
        elif (hand == 'Flush'):
            hand = self.CheckFlush(hand, hand_values)
        elif (hand == 'Full House'):
            hand = self.CheckHouse(hand, hand_values)
        elif (hand == 'Four of a Kind'):
            hand = self.CheckFour(hand, rank)
        elif (hand == 'Straight Flush'):
            hand = self.CheckStraight(hand, hand_values)
        
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
            elif (hand_values.count(value) == 3):
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

    def CheckPair(self, hand, rank):
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
        elif (rank > 4865):
            hand += ' of Sevens.'
        elif (rank > 4645):
            hand += ' of Eights.'
        elif (rank > 4425):
            hand += ' of Nines.'
        elif (rank > 4205):
            hand += ' of Tens.'
        elif (rank > 3985):
            hand += ' of Jacks.'
        elif (rank > 3765):
            hand += ' of Queens.'
        elif (rank > 3545):
            hand += ' of Kings.'
        else:
            hand += ' of Aces.'
        
        return hand
    
    def CheckThree(self, hand, rank):
        if (rank > 2401):
            hand += ' Deuces.'
        elif (rank > 2335):
            hand += ' Threes.'
        elif (rank > 2269):
            hand += ' Fours.'
        elif (rank > 2203):
            hand += ' Fives.'
        elif (rank > 2137):
            hand += ' Sixes.'
        elif (rank > 2071):
            hand += ' Sevens.'
        elif (rank > 2005):
            hand += ' Eights.'
        elif (rank > 1939):
            hand += ' Nines.'
        elif (rank > 1873):
            hand += ' Tens.'
        elif (rank > 1807):
            hand += ' Jacks.'
        elif (rank > 1741):
            hand += ' Queens.'
        elif (rank > 1675):
            hand += ' Kings.'
        else:
            hand += ' Aces.'
        
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
