
from flask import Flask, request, redirect, render_template
from auth_man_module import AuthenticationManager

#running the app will make any end points that we define available to the client
app = Flask(__name__)


@app.get("/toptrumps")
def get_login():
    return render_template("login.html")

# @app.get("/login/commit")
# def post_login():
#     username = request.args.get('username')
#     pin = request.args.get('pin')
#     auth_manager = AuthenticationManager(username, pin)
#     respon = auth_manager.authenticate()
#     if respon["status"]:
#         code = respon["authcode"]
#         url = f'http://127.0.0.1:5000/toptrumps/{code}'
#         return redirect(url)
#     else:
#         return render_template("unsucessful_login.html")

# @app.get("/toptrumps/<string:authcode>")
# def get_toptrumps(authcode):
#     if authcode == "y0Uh@v3Acc3ss":
#         return redirect("http://toptrumps")
#     else:
#         return render_template("login.html")

# @app.get("/login/commit")
# def post_login():
#     username = request.args.get('username')
#     pin = request.args.get('pin')
#     auth_manager = AuthenticationManager(username, pin)
#     respon = auth_manager.authenticate()
#     if respon["status"]:
#         return redirect("http://127.0.0.1:5000/toptrumps")
#     else:
#         return render_template("unsucessful_login.html")

# @app.get("/toptrumps")
# def get_toptrumps():
#     return render_template("toptrumps.html")

@app.get("/toptrumps/play")
def post_login():
    username = request.args.get('username')
    pin = request.args.get('pin')
    auth_manager = AuthenticationManager(username, pin)
    respon = auth_manager.authenticate()
    if respon["status"]:
        return render_template("toptrumps.html")
    else:
        return render_template("unsucessful_login.html")
