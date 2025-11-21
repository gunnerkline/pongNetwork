# =================================================================================================
# Contributing Authors:	    Gunner Kline, Nick Stone, Rebecca Mukeba
# Email Addresses:          gkl230@uky.edu, 
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading
import json # For ease of setting up received sends

clients = []

def handle_client(CONN, ADDR):
    print(f"[NEW CONNECTION] {ADDR}")
    # Send to clients screen width, height & player paddle, "left or "right
    index = clients.index(CONN)

    if index == 0:
        role = "left"
    else:
        role = "right"

    config = {
        "screenWidth": 640,
        "screenHeight": 480,
        "pad": role
    }

    try:
        CONN.send(json.dumps(config).encode())
    except:
        pass


    while True:
        try:
            text = CONN.recv(1024)
            if not text:
                break
        except:
            break
        # cleanup after disconnect
    CONN.close()
    if CONN in clients:
        clients.remove(CONN)
    print(f"[DISCONNECTED] {ADDR}")

HOST = "127.0.0.1"
PORT = 65432

pongServer_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4. UDP as this is intended for a game.
pongServer_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow for instant reuse of addresses after server restart.

pongServer_Socket.bind((HOST, PORT))
pongServer_Socket.listen()

while True:
    CONN, ADDR = pongServer_Socket.accept()
    clients.append(CONN)
    thread = threading.Thread(target=handle_client, args=(CONN, ADDR))
    thread.start()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games