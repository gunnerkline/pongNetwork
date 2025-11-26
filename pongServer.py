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

HOST = "127.0.0.1"
PORT = 65432

pongServer_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4. UDP as this is intended for a game.

pongServer_Socket.bind((HOST, PORT))

clients = []
buffers = {}
global_sync = 0

players = {
    "left": None,
    "right": None
}

while True:
    try:
        DATA, ADDR = pongServer_Socket.recvfrom(4096)
    except ConnectionResetError:
        continue

    # Insert a new client in the list and assign a configuration of paddle ownership and screen dimensions.
    if ADDR not in clients:
        clients.append(ADDR)
        buffers[ADDR] = ""
        print(f"[NEW CONNECTION] {ADDR}")

        index = clients.index(ADDR)

        if players["left"] is None:
            players["left"] = ADDR
            pad = "left"
        elif players["right"] is None:
            players["right"] = ADDR
            pad = "right"

        config = {
        "screenWidth": 640,
        "screenHeight": 480,
        "pad": pad
        }

        pongServer_Socket.sendto(json.dumps(config).encode(), ADDR)
        continue

    # Receive Client buffer containing paddle, ball location, and score
    try:
        buffers[ADDR] += DATA.decode()
    except:
        continue

    while "\n" in buffers[ADDR]:
        msg, buffers[ADDR] = buffers[ADDR].split("\n", 1)
        msg = msg.strip()
        if not msg:
            continue

        try:
            clientConfig = json.loads(msg)

            global_sync += 1
            clientConfig["sync"] = global_sync
        except:
            continue

        # In order for Authorative to work
        if "disconnect" in clientConfig:
            print(f"[DISCONNECT FROM] {ADDR}")

            if ADDR == players["left"]:
                players["left"] = None
            elif ADDR == players["right"]:
                players["right"] = None

            if ADDR in clients:
                clients.remove(ADDR)

        # Determine opponent explicitly
        # The first player to connect is considered "Authoritative," and sends its ball location and score to all other clients.
        if ADDR == players["left"]:
            otherClient = players["right"]
        elif ADDR == players["right"]:
            otherClient = players["left"]
            clientConfig.pop("ballCoords", None)
            clientConfig.pop("currentLeftScore", None)
            clientConfig.pop("currentRightScore", None)
        else:
            clientConfig.pop("ballCoords", None)
            clientConfig.pop("currentLeftScore", None)
            clientConfig.pop("currentRightScore", None)
            continue  # spectators ignored

        if otherClient is None:
            continue  # opponent not connected yet

        pongServer_Socket.sendto(
            (json.dumps(clientConfig) + "\n").encode(),
            otherClient
        )

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games