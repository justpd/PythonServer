import threading

from deuces import Card
from deuces import Deck
from deuces import Evaluator

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
                session = Session(self.Clients[0], self.Clients[1], self.roomID + 1)
                self.Sessions[session.roomID] = session
                self.Clients = self.Clients[2:]


class Session:
    def __init__(self, player_session_1, player_session_2, roomID):
        self.player_session_1 = player_session_1[0]
        self.player_session_2 = player_session_2[0]
        self.roomID = roomID

        self.chips = 500
        self.levels = [10,20,30,40,50,60,70,80,90,100,200,300,400,500]
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
            self.current_hand = self.GetStarterHand(self.current)
            self.SimulateMove(self.current_hand)
        else:
            print(cards_repr[-2:] + ' > ' + cards_repr[:2])
            print(self.player_session_2['login'] + ' is dealer.')
            self.dealer = self.player_session_2
            self.current = self.player_session_1
            self.current_hand = self.GetStarterHand(self.current)
            self.SimulateMove(self.current_hand)
        
        
        
        hand = self.GetStarterHand(self.dealer)
        self.SimulateMove(hand)
    
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
            '[', '').replace(']', '').replace(' ', '').replace(',', '  ').strip()
        
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

