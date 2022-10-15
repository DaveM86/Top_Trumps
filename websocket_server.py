import asyncio
import websockets
import json
from game import Game

# Place holder for variable assigned to an instance of class Game()
game = []

# Global websockets groups
player1_set = set()
player2_set = set()
broadcast_group = set()

async def send_message(websocket, type, value):
    try:
        for websocket in websocket:
            await websocket.send(json.dumps({"type": type, "value": value}))  
    except TypeError:
        await websocket.send(json.dumps({"type": type, "value": value}))

async def dist_game_state():
    await send_message(player1_set, "hand", str(game.player1_hand))
    await send_message(player1_set, "card", str(game.player1_current_card))

    await send_message(player2_set, "hand", str(game.player2_hand))
    await send_message(player2_set, "card", str(game.player2_current_card))

async def replay(player2):

    await send_message(player2, "hand", str(game.player2_hand))
    await send_message(player2, "card", str(game.draw_player2_card()))
   
    await play(player2)

async def play(websocket):

    async for message in websocket:
        event = json.loads(message)
        # Need to iterate cycle through the players here maybe with itertools
        if event["player"] == "player1":
            
            outcome = game.play_hand(event["attr"])
            
            await send_message(broadcast_group, "info", outcome)

            if len(game.player1_hand) != 0 and len(game.player2_hand) != 0:            
                game.draw_player1_card()
                game.draw_player2_card()

                await dist_game_state()

            elif len(game.player2_hand) == 0:
                await send_message(broadcast_group, "info", "Player1 has won the game")
                await dist_game_state()
                break
            
            else:
                await send_message(broadcast_group, "info", "Player2 has won the game")
                await dist_game_state()
                break

async def game_setup(player1):

    global game

    # Place holder for csv file or db query.
    deck = [
        [{'name':'paul', 'attr': {'atter1':7, 'atter2': 7}}],
        [{'name':'ryan', 'attr': {'atter1':4, 'atter2': 10}}],
        [{'name':'jack', 'attr': {'atter1':5, 'atter2': 8}}],
        [{'name':'david', 'attr': {'atter1':6, 'atter2': 5}}],
        ]

    game = Game(deck)
    
    game.deal()

    await send_message(player1, "hand", str(game.player1_hand))
    await send_message(player1, "card", str(game.draw_player1_card()))

    await play(player1)
    
async def add_player1(player1):
    
    player1_set.add(player1)
    broadcast_group.add(player1)

    await send_message(player1, "connect", "player1")
    await send_message(player1, "info", "Player1 has joined the game")

    await game_setup(player1)
    
async def add_player2(player2):
    
    player2_set.add(player2)
    broadcast_group.add(player2)

    await send_message(player2, "connect", "player2")
    await send_message(player2, "info", "Player2 has joined the game")
    
    await replay(player2)

async def handler(websocket, path):

    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if len(player1_set) == 0:
        await add_player1(websocket)
    
    elif len(player2_set) == 0:
        await add_player2(websocket)

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
