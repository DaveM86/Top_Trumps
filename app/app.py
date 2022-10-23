from flask import Flask, request, render_template
from auth_man_module import AuthenticationManager


#running the app will make any end points that we define available to the client
app = Flask(__name__)


@app.get("/login")
def get_login():
    # Change the url back to login.html after testing.
    return render_template("login.html")

@app.post("/toptrumps")
def post_login():
    username = request.form.get("username", "")
    pin = request.form.get("pin", "")
    auth_manager = AuthenticationManager(username, pin)
    respon = auth_manager.authenticate()
    if respon["status"]:
        return render_template("toptrumps.html")
    else:
        return render_template("unsucessful_login.html")

@app.get("/disconnected")
def get_waitingroom():
    return render_template("disconnected.html")

