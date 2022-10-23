'''
Class to modify the behaviour of the players toptrumps hand throughout the game.
'''

import random

class Game():
    def __init__(self, deck):
        self.deck = deck
        self.player1_hand = []
        self.player2_hand = []
        self.player1_current_card = []
        self.player2_current_card = []
        self.draw_card_store = []
        self.current_player = ["player1"]
        self.next_player = ["player2"]

    def turn(self):
        # Rotate the players between current player and next player.
        self.current_player.append(self.next_player.pop(0))
        self.next_player.append(self.current_player.pop(0))
    
    def deal(self):
        # Shuffle and deal the pack between the two players.
        player_hands = [self.player1_hand, self.player2_hand]
        random.shuffle(self.deck)
        while len(self.deck) != 0:
            for player_hand in player_hands:
                if len(self.deck) == 0:
                    break
                else:
                    player_hand += self.deck.pop()
    
    def draw_player1_card(self):
        # Draw next card Player1
        self.player1_current_card.append(self.player1_hand.pop(0))
        return self.player1_current_card

    def draw_player2_card(self):
        # Draw next card Player2
        self.player2_current_card.append(self.player2_hand.pop(0))
        return self.player2_current_card
    
    def play_hand(self, attribute):
        # Compare the players card on selected attributes and detrmin outcome of game.
        if self.player1_current_card[0]["attr"][attribute] > self.player2_current_card[0]["attr"][attribute]:

            self.player1_hand.append(self.player1_current_card.pop())
            self.player1_hand.append(self.player2_current_card.pop())
            for x in range(len(self.draw_card_store)):
                self.player1_hand.append(self.draw_card_store.pop())
            
            return "Player 1 has won that round"
       
        elif self.player1_current_card[0]["attr"][attribute] < self.player2_current_card[0]["attr"][attribute]:

            self.player2_hand.append(self.player1_current_card.pop())
            self.player2_hand.append(self.player2_current_card.pop())
            for x in range(len(self.draw_card_store)):
                self.player2_hand.append(self.draw_card_store.pop())
            
            return "Player 2 has won that round"
        
        else:
            self.draw_card_store.append(self.player1_current_card.pop())
            self.draw_card_store.append(self.player2_current_card.pop())

            return "That round was a draw"