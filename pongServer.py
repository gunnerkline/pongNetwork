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
    # Send to clients screen width, height & player paddle, "left or "right
    for c in clients:
        if c == clients[1]:
            c.send(json.dumps({"screenWidth" : 640, "screenHeight" : 480, "pad" : "left"})).encode()
        if c == clients[2]:
            c.send(json.dumps({"screenWidth" : 640, "screenHeight" : 480, "pad" : "right"})).encode()
            
    print(f"[NEW CONNECTION] {ADDR}")
    while True:
        try:
            msg = CONN.recv(1024)
            if not msg:  # client disconnected
                break
            # broadcast message to everyone except the sender
            for c in clients:
                if c != CONN:
                    c.send(msg)
        except:
            break
        # cleanup after disconnect
    CONN.close()
    if CONN in clients:
        clients.remove(CONN)
    print(f"[DISCONNECTED] {ADDR}")

HOST = "0.0.0.0"
PORT = 12500

pongServer_Socket = socket.socket(socket.AF_INET, socket.DGRAM) # IPv4. UDP as this is intended for a game.
pongServer_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow for instant reuse of addresses after server restart.

pongServer_Socket.bind(HOST, PORT)
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