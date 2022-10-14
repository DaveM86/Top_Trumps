'''
Top Trumps Project websocket server.
'''

import asyncio
import websockets
import random
import json

player1 = set()
player2 = set()
broadcast_group = set()
player1_hand = []
player2_hand = []

async def play():
    
    player1_current_card = []
    player1_current_card.append(player1_hand.pop())
    player2_current_card = []
    player2_current_card.append(player2_hand.pop())
    for player in player1:
        await player.send(json.dumps({"type": "card", "value": str(player1_current_card)}))
    for player in player2:
        await player.send(json.dumps({"type": "card", "value": str(player2_current_card)}))

'''

    async for player in broadcast_group:
        async for message in player:
            event = json.loads(message)
            if event["type"] == "move":
                player1_current_card = []
                player1_current_card.append(player1_hand.pop())
                player2_current_card = []
                player2_current_card.append(player2_hand.pop())
                for player in player1:
                    await player.send(json.dumps({"type": "card", "value": str(player1_current_card)}))
                for player in player2:
                    await player.send(json.dumps({"type": "card", "value": str(player2_current_card)}))

'''

async def game_setup():
    
    pack = [
        [{'name':'paul', 'attr': {'atter1':7, 'atter2': 7}}],
        [{'name':'ryan', 'attr': {'atter1':4, 'atter2': 10}}],
        [{'name':'jack', 'attr': {'atter1':5, 'atter2': 8}}],
        [{'name':'david', 'attr': {'atter1':6, 'atter2': 5}}],
        [{'name':'frosty', 'attr': {'atter1':7, 'atter2': 7}}],
        [{'name':'russ', 'attr': {'atter1':4, 'atter2': 10}}],
        [{'name':'bruce', 'attr': {'atter1':5, 'atter2': 8}}],
        [{'name':'kath', 'attr': {'atter1':6, 'atter2': 5}}]
        ]

    player_hands = [player1_hand, player2_hand]
    random.shuffle(pack)

    while len(pack) != 0:
        for player_hand in player_hands:
            if len(pack) == 0:
                break
            else:
                player_hand += pack.pop()

    for player in player1:
        await player.send(json.dumps({"type": "hand", "value": str(player1_hand)}))
    for player in player2:
        await player.send(json.dumps({"type": "hand", "value": str(player2_hand)}))
    
    await play()
    
async def add_player1(player):
        player1.add(player)
        broadcast_group.add(player)

        for player in player1:
            await player.send(json.dumps({"type": "connect", "value": "player1"}))
            await player.send(json.dumps({"type": "info", "value": "Player1 has joined the game"}))
    
async def add_player2(player):
        player2.add(player)
        broadcast_group.add(player)

        for player in player2:
            await player.send(json.dumps({"type": "connect", "value": "player2"}))
            await player.send(json.dumps({"type": "info", "value": "Player2 has joined the game"}))

        await game_setup()

async def handler(websocket, path):

    print('A client has connected to the server.')

    while len(player2) == 0:
        async for message in websocket:
            event = json.loads(message)
            if event["type"] == "init":
                print(message)
                if len(player1) == 0:
                    await add_player1(websocket)
                elif websocket not in player1:
                    await add_player2(websocket)

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
