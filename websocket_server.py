import asyncio
import websockets
import random
import json

player1 = set()
player2 = set()
broadcast_group = set()
player1_hand = []
player2_hand = []
player1_current_card = []
player2_current_card = []
draw_card_store = []


async def replay(websocket):

    for player in player2:
        await player.send(json.dumps({"type": "hand", "value": str(player2_hand)}))
        await player.send(json.dumps({"type": "card", "value": str(player2_current_card)}))
    
    await play(websocket)

async def play(websocket):

    async for message in websocket:
        event = json.loads(message)
        if event["player"] == "player1":
            print(message)
            
            if player1_current_card[0]["attr"][event["attr"]] > player2_current_card[0]["attr"][event["attr"]]:
                for player in broadcast_group:
                    await player.send(json.dumps({"type": "info", "value": "Player1 has won that round"}))
                player1_hand.append(player1_current_card.pop())
                player1_hand.append(player2_current_card.pop())
                for x in range(len(draw_card_store)):
                    player1_hand.append(draw_card_store.pop())
            elif player1_current_card[0]["attr"][event["attr"]] < player2_current_card[0]["attr"][event["attr"]]:
                for player in broadcast_group:
                    await player.send(json.dumps({"type": "info", "value": "Player2 has won that round"}))
                player2_hand.append(player1_current_card.pop())
                player2_hand.append(player2_current_card.pop())
                for x in range(len(draw_card_store)):
                    player2_hand.append(draw_card_store.pop())
            else:
                for player in broadcast_group:
                    await player.send(json.dumps({"type": "info", "value": "Round was a draw"}))
                draw_card_store.append(player1_current_card.pop())
                draw_card_store.append(player2_current_card.pop())

            if len(player1_hand) != 0 and len(player2_hand) != 0:            
                player1_current_card.append(player1_hand.pop(0))
                player2_current_card.append(player2_hand.pop(0))

                for player in player1:
                    await player.send(json.dumps({"type": "hand", "value": str(player1_hand)}))
                    await player.send(json.dumps({"type": "card", "value": str(player1_current_card)}))

                for player in player2:
                    await player.send(json.dumps({"type": "hand", "value": str(player2_hand)}))
                    await player.send(json.dumps({"type": "card", "value": str(player2_current_card)}))
            elif len(player2_hand) == 0:
                for player in broadcast_group:
                    await player.send(json.dumps({"type": "info", "value": "Player1 has won the game"}))
                for player in player1:
                    await player.send(json.dumps({"type": "hand", "value": str(player1_hand)}))
                    await player.send(json.dumps({"type": "card", "value": str(player1_current_card)}))

                for player in player2:
                    await player.send(json.dumps({"type": "hand", "value": str(player2_hand)}))
                    await player.send(json.dumps({"type": "card", "value": str(player2_current_card)}))
                break
            else:
                for player in broadcast_group:
                    await player.send(json.dumps({"type": "info", "value": "Player2 has won the game"}))
                for player in player1:
                    await player.send(json.dumps({"type": "hand", "value": str(player1_hand)}))
                    await player.send(json.dumps({"type": "card", "value": str(player1_current_card)}))

                for player in player2:
                    await player.send(json.dumps({"type": "hand", "value": str(player2_hand)}))
                    await player.send(json.dumps({"type": "card", "value": str(player2_current_card)}))
                break

            

async def game_setup(player):

    player1.add(player)
    broadcast_group.add(player)

    for player in player1:
        await player.send(json.dumps({"type": "connect", "value": "player1"}))
        await player.send(json.dumps({"type": "info", "value": "Player1 has joined the game"}))
    
    pack = [
        [{'name':'paul', 'attr': {'atter1':7, 'atter2': 7}}],
        [{'name':'ryan', 'attr': {'atter1':4, 'atter2': 10}}],
        [{'name':'jack', 'attr': {'atter1':5, 'atter2': 8}}],
        [{'name':'david', 'attr': {'atter1':6, 'atter2': 5}}],
        ]

    player_hands = [player1_hand, player2_hand]
    random.shuffle(pack)

    while len(pack) != 0:
        for player_hand in player_hands:
            if len(pack) == 0:
                break
            else:
                player_hand += pack.pop()
    
    player1_current_card.append(player1_hand.pop(0))
    player2_current_card.append(player2_hand.pop(0))

    for player in player1:
        await player.send(json.dumps({"type": "hand", "value": str(player1_hand)}))
        await player.send(json.dumps({"type": "card", "value": str(player1_current_card)}))

    await play(player)
    
async def add_player2(player):
    player2.add(player)
    broadcast_group.add(player)

    for player in player2:
        await player.send(json.dumps({"type": "connect", "value": "player2"}))
        await player.send(json.dumps({"type": "info", "value": "Player2 has joined the game"}))
    
    await replay(player)

async def handler(websocket, path):

    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if len(player1) == 0:
        await game_setup(websocket)
    
    elif len(player2) == 0:
        await add_player2(websocket)

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
