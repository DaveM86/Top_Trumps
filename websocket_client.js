let player;

function initPlayer(websocket) {
  websocket.addEventListener("open", () => {
    // Send an "init" event according to who is connecting.
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    websocket.send(JSON.stringify(event));
  });
}



function receiveMessages(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "connect":
        document.querySelector(".connect").textContent = event.value;
        player = event.value;
        break;
      case "info":
        document.querySelector(".info").textContent = event.value;
        break;
        case "hand":
          document.querySelector(".hand").textContent = event.value;
          break;
        case "card":
          document.querySelector(".card").textContent = event.value;
          break;
      default:
        console.error("unsupported event", event);
    }
  });
}

function sendMove(websocket) {
  document.querySelector(".plus").addEventListener("click", () => {
    websocket.send(JSON.stringify({ "type": "move", "player": player, "attr": "atter1" }));
  });
}

window.addEventListener("DOMContentLoaded", () => {
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://localhost:8001/");
  initPlayer(websocket);
  receiveMessages(websocket);
  sendMove(websocket);
});

