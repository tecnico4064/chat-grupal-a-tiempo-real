from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
app.secret_key = "secreto"
socketio = SocketIO(app, cors_allowed_origins="*")

USUARIOS_FILE = "usuarios.json"
CHAT_FILE = "chat.json"

def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as file:
            return json.load(file)
    return {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w") as file:
        json.dump(usuarios, file, indent=4)

def cargar_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as file:
            return json.load(file)
    return []

def guardar_chats(chats):
    with open(CHAT_FILE, "w") as file:
        json.dump(chats, file, indent=4)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        usuarios = cargar_usuarios()
        if usuario in usuarios:
            return "El usuario ya existe"
        usuarios[usuario] = clave
        guardar_usuarios(usuarios)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        usuarios = cargar_usuarios()
        if usuario in usuarios and usuarios[usuario] == clave:
            session["usuario"] = usuario
            return redirect(url_for("chat"))
        return "Usuario o contraseña incorrectos"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

@app.route("/chat")
def chat():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", usuario=session["usuario"])

@socketio.on("send_message")
def handle_message(data):
    mensaje = {"usuario": session.get("usuario", "Anónimo"), "mensaje": data}
    chats = cargar_chats()
    chats.append(mensaje)
    guardar_chats(chats)
    emit("receive_message", mensaje, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
