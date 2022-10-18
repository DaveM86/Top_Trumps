import asyncio
from multiprocessing.connection import Client
import websockets
import json
from game import Game

# Place holder for variable assigned to an instance of class Game().
game = []

# Global websockets groups.
player1_set = set()
player2_set = set()
broadcast_group = set()

async def send_message(websocket, type, value):
    # Formats and sends messages to the clients.
    try:
        # Will will extract websockets from a set() before sending messages.
        for websocket in websocket:
            await websocket.send(json.dumps({"type": type, "value": value}))  
    except TypeError:
        # If the websocket arg isn't a set() will not loop though it and send the message directly.
        await websocket.send(json.dumps({"type": type, "value": value}))

async def disconnect_seq():
    # Resets the game after a disconnection.
    
    global broadcast_group, player1_set, player2_set
    
    try:
        counter = [x for x in range(5+1)][::-1]
        
        for num in counter:
            await send_message(
                    broadcast_group,
                    "info",
                    f"Your opponent has left the game and you are going to be disconnected in {num} seconds."
                    )
            await asyncio.sleep(2)      

        await send_message(broadcast_group, "redirect", "http://localhost:5000/login")
        player1_set = set()
        player2_set = set()
        broadcast_group = set()
    
    except:
        player1_set = set()
        player2_set = set()
        broadcast_group = set()

async def distribute_game_state():
    await send_message(player1_set, "hand", str(game.player1_hand))
    await send_message(player1_set, "card", str(game.player1_current_card))

    await send_message(player2_set, "hand", str(game.player2_hand))
    await send_message(player2_set, "card", str(game.player2_current_card))

async def replay(player2):
    # As the first hand is delt before Player2 joins the game
    # this allow Player2 to access first hand before joing the game.
    await send_message(player2, "hand", str(game.player2_hand))
    await send_message(player2, "card", str(game.draw_player2_card()))
   
    await play(player2)

async def play(websocket):
    # The main game loop for toptrumps.

    turn = ["player1", "player2"]
    last_played = "player1"

    try:

        async for message in websocket:

            # connection test, if this fails the exception will be raised.
            await send_message(broadcast_group, "test", "ignore this message")
            
            event = json.loads(message)
            
            # Need to iterate cycle through the players here maybe with itertools.
            turn_hold = turn.pop(0)
            turn.append(turn_hold)

            if event["type"] == "move" and event["player"] == turn[0] and last_played == turn[1]:
                
                outcome = game.play_hand(event["attr"])

                await send_message(broadcast_group, "info", outcome)

                # Test if game is still in play if not broadcast winner.
                if len(game.player1_hand) != 0 and len(game.player2_hand) != 0:            
                    game.draw_player1_card()
                    game.draw_player2_card()
                    last_played = turn[0]

                    await distribute_game_state()

                elif len(game.player2_hand) == 0:
                    await send_message(broadcast_group, "info", "Player1 has won the game")
                    await distribute_game_state()
                    await asyncio.sleep(3)
                    await disconnect_seq()
                    break
                
                else:
                    await send_message(broadcast_group, "info", "Player2 has won the game")
                    await distribute_game_state()
                    await asyncio.sleep(3)
                    await disconnect_seq()
                    break
    
    except websockets.exceptions.ConnectionClosedOK:
        # Handeling disconnection during the game play.
        
        disconnected_client = set()
        
        # Find the disconnected client, assumes that the message that has
        # triggered the error is from the reamining connected client.
        for client in broadcast_group:
            if client is not websocket:
                disconnected_client.add(client)
        
        for client in disconnected_client:
            broadcast_group.remove(client)
            del(disconnected_client)
        
        # Call the disconnection sequence.
        await disconnect_seq()

    except websockets.exceptions.ConnectionClosedError:
        # Handeling disconnection during the game play.
        
        disconnected_client = set()
        
        # Find the disconnected client, assumes that the message that has
        # triggered the error is from the reamining connected client.
        for client in broadcast_group:
            if client is not websocket:
                disconnected_client.add(client)
        
        for client in disconnected_client:
            broadcast_group.remove(client)
            del(disconnected_client)
        
        # Call the disconnection sequence.
        await disconnect_seq()



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
    # Adds Player1 to the game and messaging groups.
    
    player1_set.add(player1)
    broadcast_group.add(player1)

    await send_message(player1, "connect", "player1")
    await send_message(player1, "info", "Player1 has joined the game")

    # Calss the games set-up.
    await game_setup(player1)
    

async def add_player2(player2):
    # Adds Player2 to the game.
    
    player2_set.add(player2)
    broadcast_group.add(player2)

    await send_message(player2, "connect", "player2")
    await send_message(player2, "info", "Player2 has joined the game")
    
    await replay(player2)

async def handler(websocket):
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if len(player1_set) == 0:
        await add_player1(websocket)    
    elif len(player2_set) == 0:
        await add_player2(websocket)
    else:
        await send_message(
            websocket,
            "info",
            "Sorry, the deck is in use at the moment please come back later."
            )

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
