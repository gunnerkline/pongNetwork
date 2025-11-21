# =================================================================================================
# Contributing Authors:	    Gunner Kline, Nick Stone, Rebecca Mukeba
# Email Addresses:          gkl230@uky.edu, 
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

clients = []

HOST = "0.0.0.0"
PORT = 12500

pongServer_Socket = socket.socket(socket.AF_INET, socket.DGRAM) # IPv4. Connectionless as this is intended for a game.
pongServer_Socket.bind(HOST, PORT)
pongServer_Socket.listen()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games