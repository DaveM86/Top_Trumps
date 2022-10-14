# Top Trumps
Top Trumps Project

### Project Notes

I've removed most of the game play code while we get the messaging sorted, hoping this should be enough to start with.
I've left the client.js file in there if you want to use it as a tarting point. Totally open to adding diffrent messaging "types" or changing the structure
as you think we need.

#### Requirements

The only python requirement if "websockets"..... pip install websockets 

### Messages

All message between the server and the client should be json in the form

{"type": "type value", "value": "value value"}

e.g.

{"type": "card", "value": "{"name":"jack", "attr": {"attr1": 5, "attr2": 10}}"}

### Server to Client Messages

Types Include:

connect - assign player name, either player1 or player2

info - generic info e.g. "you have joined the game" or "Player1 to take a turn"

hand - dictionary of all cards in players hand

card - dictionary of players current card
  
### Client to Server Messages

Types Include:

init - needs to be included in intitial message to server to initialilase player in the game

move - to indicate when player makes a move, the value of the this type should be attribute "attractivness"

### Running

Run the websocket_server.py file from a terminal and open the app.html in two browsers.
