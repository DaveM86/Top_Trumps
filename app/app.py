
from flask import Flask, jsonify, request, redirect, render_template
from auth_man_module import AuthenticationManager
import json

#running the app will make any end points that we define available to the client
app = Flask(__name__)


@app.get("/login")
def get_login():
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

@app.get("/waitingroom")
def get_waitingroom():
    return render_template("waitingroom.html")

# @app.get("/toptrumps/play")
# def post_login():
#     username = request.args.get('username')
#     pin = request.args.get('pin')
#     auth_manager = AuthenticationManager(username, pin)
#     respon = auth_manager.authenticate()
#     if respon["status"]:
#         return render_template("toptrumps.html")
#     else:
#         return render_template("unsucessful_login.html")
