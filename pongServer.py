# =================================================================================================
# Contributing Authors:	    Gunner Kline
# Email Addresses:          gkl230@uky.edu, 
# Date:                     11/26/2025
# Purpose:                  Handle receiving and sending of crucial data i.e. paddle and ball locations across multiple clients. Discern between players and spectators.
# Misc:                     
# =================================================================================================

import socket
import json

HOST = "127.0.0.1"
PORT = 62222

pongServer_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4. UDP as this is intended for a game.

pongServer_Socket.bind((HOST, PORT))

clients = []
spectators = []
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
        else:
            spectators.append(ADDR)
            pad = "spectator"

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
        except json.JSONDecodeError:
            continue

        # ---- Disconnect handling ----
        if "disconnect" in clientConfig:
            print(f"[DISCONNECT FROM] {ADDR}")

            for key in ["left", "right"]:
                if players[key] == ADDR:
                    players[key] = None

            if ADDR in spectators:
                spectators.remove(ADDR) if ADDR in spectators else None
            if ADDR in clients:
                clients.remove(ADDR)
            if ADDR in buffers:
                del buffers[ADDR]

            # skip sending to other clients
            break  # exit the while "\n" loop

        # Determine opponent and spectators
        # The first player to connect is considered "Authoritative," and sends its ball location and score to all other clients.

        recipients = []
        if ADDR == players["left"]:
            if players["right"]:
                recipients.append(players["right"])
        elif ADDR == players["right"]:
            if players["left"]:
                recipients.append(players["left"])

                clientConfig.pop("ballCoords", None)
                clientConfig.pop("currentLeftScore", None)
                clientConfig.pop("currentRightScore", None)

        recipients.extend(spectators)

        for r in recipients:
            pongServer_Socket.sendto((json.dumps(clientConfig) + "\n").encode(), r)

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games