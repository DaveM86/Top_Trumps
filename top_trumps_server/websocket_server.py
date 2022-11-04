import asyncio
import websockets
import json
from game import Game
from logger import info_logger
from state_checker import inplay_idle_check
import pandas as pd

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
    # Resets the game after a disconnection during the game.

    global broadcast_group, player1_set, player2_set

    try:
        counter = [x for x in range(5 + 1)][::-1]

        for num in counter:
            await send_message(
                broadcast_group,
                "info",
                f"You are going to be disconnected in {num} seconds.",
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


async def immedaite_disconnect():
    # Resets the game if it's found to be idle when a new connections is recieved.
    
    global broadcast_group, player1_set, player2_set
    
    await send_message(
        broadcast_group, "redirect", "http://localhost:5000/disconnected"
    )
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

    await send_message(player2, "card", str(game.draw_player2_card()))
    await send_message(player2, "hand", str(game.player2_hand))
    
    await play(player2)


async def play(websocket):
    # The main game loop for toptrumps.
    try:

        async for message in websocket:
            # connection test, if this fails the exception will be raised.
            await send_message(broadcast_group, "test", "ignore this message")

            event = json.loads(message)

            # Need to iterate cycle through the players here maybe with itertools.

            if event["type"] == "move" and event["player"] == game.next_player[0]:

                # Log message
                info_logger(websocket, event)

                outcome = game.play_hand(event["attr"])

                await send_message(broadcast_group, "info", outcome)

                # Test if game is still in play if not broadcast winner.
                if len(game.player1_hand) != 0 and len(game.player2_hand) != 0:
                    game.draw_player1_card()
                    game.draw_player2_card()
                    game.turn()

                    await distribute_game_state()

                elif len(game.player2_hand) == 0:
                    await send_message(
                        broadcast_group, "info", "Player1 has won the game"
                    )
                    await distribute_game_state()
                    await asyncio.sleep(3)
                    await disconnect_seq()
                    break

                else:
                    await send_message(
                        broadcast_group, "info", "Player2 has won the game"
                    )
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
            del disconnected_client

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
            del disconnected_client

        # Call the disconnection sequence.
        await disconnect_seq()

def create_deck():
    
    df = pd.read_csv("cards.csv")
    deck = df.to_dict('records')
    return(deck)

async def game_setup(player1):

    global game

    deck = create_deck()
    game = Game(deck)

    game.deal()

    await send_message(player1, "card", str(game.draw_player1_card()))
    await send_message(player1, "hand", str(game.player1_hand))
    
    await play(player1)


async def add_player2(player2):
    # Add Player2 to the game.

    player2_set.add(player2)
    broadcast_group.add(player2)

    await send_message(player2, "connect", "player2")
    await send_message(player2, "info", "Player2 has joined the game")

    await replay(player2)


async def add_player1(player1):
    # Add Player1 to the game and messaging groups.

    player1_set.add(player1)
    broadcast_group.add(player1)

    await send_message(player1, "connect", "player1")
    await send_message(player1, "info", "Player1 has joined the game")

    # Initialise the games set-up.
    await game_setup(player1)


async def allocate_player(websocket):
    # Asign player1
    if len(player1_set) == 0:
        await add_player1(websocket)

    # Asign player2
    elif len(player2_set) == 0:
        await add_player2(websocket)

    # If game is play send message asking to come back later.
    else:
        await send_message(
            websocket,
            "info",
            "Sorry, the deck is in use at the moment please come back later.",
        )


async def run_test_conditions():
    # Run test connditions to see if game is still in play.

    # If player1 is present and player2 is not 
    # check to see if the idle connection time is greater than 5 mins
    if len(player1_set) != 0 and len(player2_set) == 0:
        if inplay_idle_check("Player1 has joined the game", 0, 1, False):
            await immedaite_disconnect()

    # if both player1 and player2 are present
    # check to see how long the game has been idle
    # assumption is made that if no move has been played
    # in ten mins the game has been abandonded
    elif len(player1_set) != 0 and len(player2_set) != 0:
        if inplay_idle_check("move", 0, 1, True):
            if inplay_idle_check("Player2 has joined the game", 0, 1, True):
                await immedaite_disconnect()


async def handler(websocket):

    # Wait for connection.
    message = await websocket.recv()

    # Parse message.
    event = json.loads(message)

    # Log message.
    info_logger(websocket, event)

    # Confirm messgae type is an initial connection request.
    assert event["type"] == "init"

    # Test the status of any game currently running.
    await run_test_conditions()

    # Acclocate connected webscket to player position.
    await allocate_player(websocket)


async def main():
    async with websockets.serve(handler, "127.0.0.1", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
