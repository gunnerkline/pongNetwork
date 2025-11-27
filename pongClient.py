# =================================================================================================
# Contributing Authors:	    Gunner Kline, Rebecca Mukeba, Nick Stone
# Email Addresses:          gkl230@uky.edu, rnmu228@uky.edu, nsst231@uky.edu 
# Date:                     11/26/2025
# Purpose:                  Allow conversation between client, server, and other clients. Handle game operations, sending and receiving client configurations, synchronizations, spectators, and end-of-game design.
# Misc:                     
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import json # For ease of setting up received sends
import random # Solely for randomized music playlist

from assets.code.helperCode import *

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket,pongServer_addr:tuple[str,str]) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    pointSound.set_volume(0.3)

    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Music by Gunner Kline
    pongMusic1 = pygame.mixer.Sound("./assets/sounds/pongMusic1.mp3")
    pongMusic2 = pygame.mixer.Sound("./assets/sounds/pongMusic2.mp3")

    pongTrack = {
        pongMusic1,
        pongMusic2
        }


    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    winMessage = pygame.Rect(0,0,0,0)
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    elif playerPaddle == "right":
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle
    else:
        # For spectators
        opponentPaddleObj = None
        playerPaddleObj = None


    lScore = 0
    rScore = 0

    sync = 0
    last_received_sync = -1

    recv_buffer = ""
    client.setblocking(False)

    gameOver = False

    # Play music
    if playerPaddleObj:
        pongSong = random.choice(list(pongTrack))
        pongSong.play(loops=-1)
    else:
        pongSong

    while True:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                # Send disconnect message to server
                try:
                    client.sendto(b'{"disconnect": true}\n', pongServer_addr)
                except:
                    pass

                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if playerPaddleObj:
                    if event.key == pygame.K_DOWN:
                        playerPaddleObj.moving = "down"

                    elif event.key == pygame.K_UP:
                        playerPaddleObj.moving = "up"

                    elif event.key == pygame.K_r and gameOver:
                        gameOver = False
                        lScore = 0
                        rScore = 0

                if event.key == pygame.K_q:
                    try:
                        client.sendto(b'{"disconnect": true}\n', pongServer_addr)
                    except:
                        pass
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.KEYUP and playerPaddleObj:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements

                     
        # For players only, send essential data to the server for redistribution to other player and spectators
        if playerPaddleObj:
            config = {
                "padID"             : playerPaddle,
                "paddleCoords"      : playerPaddleObj.rect.topleft if playerPaddleObj else "NoPaddle",
                "ballCoords"        : ball.rect.topleft if playerPaddleObj else None,
                "currentLeftScore"  : lScore,
                "currentRightScore" : rScore,
                "sync"              : sync
            }
            try:
                client.sendto((json.dumps(config) +"\n").encode(),pongServer_addr)
            except:
                pass

        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        if playerPaddle != "spectator":
            for paddle in [playerPaddleObj, opponentPaddleObj]:
                if paddle is None:
                    continue
                if paddle.moving == "down":
                    if paddle.rect.bottomleft[1] < screenHeight-10:
                        paddle.rect.y += paddle.speed
                elif paddle.moving == "up":
                    if paddle.rect.topleft[1] > 10:
                        paddle.rect.y -= paddle.speed
        else:
            # For spectators, just draw both paddles
            for paddle in [leftPaddle, rightPaddle]:
                pygame.draw.rect(screen, WHITE, paddle)

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)

            playAgainLines = [
                "Play Again?",
                "R to retry",
                "Q to quit"
            ]

            # In place of pygame not being able to utilize `\n`'s
            line_height = winFont.get_linesize()
            for i, line in enumerate(playAgainLines):
                paTextSurface = winFont.render(line, False, WHITE)
                paTextRect = paTextSurface.get_rect()
                # Center horizontally, offset vertically per line
                paTextRect.center = (screenWidth/2, 3*screenHeight/4 + i*line_height)
                screen.blit(paTextSurface, paTextRect)

            gameOver = True
        else:

            # ==== Ball Logic =====================================================================
            if playerPaddle != "spectator":
                ball.updatePos()

                # If the ball makes it past the edge of the screen, update score, etc.
                if ball.rect.x > screenWidth:
                    lScore += 1
                    pointSound.play()
                    ball.reset(nowGoing="left")
                elif ball.rect.x < 0:
                    rScore += 1
                    pointSound.play()
                    ball.reset(nowGoing="right")
                
                # If the ball hits a paddle
                if ball.rect.colliderect(playerPaddleObj.rect):
                    bounceSound.play()
                    ball.hitPaddle(playerPaddleObj.rect.center[1])
                elif ball.rect.colliderect(opponentPaddleObj.rect):
                    bounceSound.play()
                    ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
                # If the ball hits a wall
                if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                    bounceSound.play()
                    ball.hitWall()
            
                pygame.draw.rect(screen, WHITE, ball)
            else:
                pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle:
                pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.update()
        clock.tick(60)

        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game

        # Inside the receive section
        latest_msg = None

        # Receive opposing player's data and put in a buffer for separating
        while True:
            try:
                packet, _ = client.recvfrom(4096)
                if not packet:
                    break
                recv_buffer += packet.decode()
            except BlockingIOError:
                break
            except ConnectionResetError:
                print("Server Disconnect")
                return

        # Framed Message Reconstruction to avoid parser or JSONDecodeError errors
        if "\n" in recv_buffer:
            parts = recv_buffer.split("\n")
            recv_buffer = parts.pop()  # Add partial messages
            for p in parts:
                p = p.strip()
                if p:
                    latest_msg = p


        if latest_msg:
            try:
                opconfig = json.loads(latest_msg)
            except json.JSONDecodeError:
                latest_msg = None
            else:
                # If an opponent's sync is newer than a players, update with their information.
                incoming_sync = opconfig.get("sync", -1)
                if incoming_sync > last_received_sync:
                    last_received_sync = incoming_sync

                    # Ball update
                    if "ballCoords" in opconfig:
                        ball.rect.topleft = opconfig["ballCoords"]

                    # Score update
                    if "currentLeftScore" in opconfig:
                        lScore = opconfig["currentLeftScore"]
                    if "currentRightScore" in opconfig:
                        rScore = opconfig["currentRightScore"]

                    # Paddle update
                    if "paddleCoords" in opconfig and "padID" in opconfig:
                        padAssigned = opconfig["padID"]

                        # If not a spectator nor a paddle that is the players, update opponent's paddle location
                        if playerPaddle != "spectator":
                            if padAssigned != playerPaddle:
                                opponentPaddleObj.rect.topleft = opconfig["paddleCoords"]
                        else:
                            # If a spectator, update both paddles
                            if padAssigned == "left":
                                leftPaddle.rect.topleft = opconfig["paddleCoords"]
                            elif padAssigned == "right":
                                rightPaddle.rect.topleft = opconfig["paddleCoords"]

        # =========================================================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Changed SOCK_STREAM to SOCK_DGRAM

    client.settimeout(5.0)

    # Get the required information from your server (screen width, height & player paddle, "left or "right)
    port = int(port);
    pongServer_addr = (ip, port) # Important for usability with UDP

    screenWidth  = None
    screenHeight = None
    pad          = None


    # Utilize errorLabel to handle error within application.
    try:
        client.sendto(json.dumps({"join": True}).encode(), pongServer_addr)

        # Receive initial configuration from server
        data, _      = client.recvfrom(4096)
        server_info  = json.loads(data.decode())
        screenWidth  = server_info["screenWidth"]
        screenHeight = server_info["screenHeight"]
        pad          = server_info["pad"]
    except socket.timeout:
        errorLabel.config(text="Error: Connection timeout. Server may be unreachable.")
        errorLabel.update()
        client.close()
        return
    except socket.gaierror:
        errorLabel.config(text="Error: Invalid IP address. Please check and try again.")
        errorLabel.update()
        client.close()
        return
    except ConnectionRefusedError:
        errorLabel.config(text="Error: Connection refused. Server may not be running.")
        errorLabel.update()
        client.close()
        return
    except json.JSONDecodeError:
        errorLabel.config(text="Error: Invalid response from server.")
        errorLabel.update()
        client.close()
        return
    except Exception as e:
        errorLabel.config(text=f"Error: {str(e)}")
        errorLabel.update()
        client.close()
        return

    # Further exceptions
    if pad not in ["left", "right", "spectator"]:
            errorLabel.config(text="Error: Invalid paddle assignment from server.")
            errorLabel.update()
            client.close()
            return
    if screenWidth == None or screenHeight == None:
            errorLabel.config(text="Error: Invalid screen dimension assignment from server.")
            errorLabel.update()
            client.close()
    

    # If you have messages you'd like to show the user use the errorLabel widget like so
    # errorLabel.config(text=f"Some update text. You input: IP: {ip}, Port: {port}")
    # You may or may not need to call this, depending on how many times you update the label
    # errorLabel.update()     

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(screenWidth, screenHeight, pad, client, pongServer_addr)  # User will be either left or right paddle
    app.quit()         # Kills the window


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    startScreen()
    
    # Uncomment the line below if you want to play the game without a server to see how it should work
    # the startScreen() function should call playGame with the arguments given to it by the server this is
    # here for demo purposes only
    # playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))