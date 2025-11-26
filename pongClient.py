
  # =================================================================================================
# Contributing Authors:	    
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  Client-side implementation for multiplayer Pong game. Handles connection
#                          to server, receives game configuration, and manages game state synchronization.
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import json # For ease of setting up received sends

from assets.code.helperCode import *

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

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
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0

    while True:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements
        
        
        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)
        else:

            # ==== Ball Logic =====================================================================
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
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.update([topWall, bottomWall, ball, leftPaddle, rightPaddle, scoreRect, winMessage])
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game

        # =========================================================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Author:       
    # Purpose:      Connect to the Pong game server, send initial connection packet, and receive
    #               configuration information (screen dimensions and paddle assignment) from the server.
    # Pre:          The server must be running and accessible at the provided IP and port.
    #               The errorLabel widget must be initialized and visible in the tkinter window.
    # Post:         A UDP socket is created and connected to the server. The client receives a JSON
    #               configuration containing screenWidth, screenHeight, and pad (paddle assignment).
    #               The game window is closed and playGame() is called with the received configuration.
    
    try:
        # Convert port string to integer
        port_num = int(port)
    except ValueError:
        errorLabel.config(text="Error: Invalid port number. Please enter a valid port.")
        errorLabel.update()
        return
    
    # Create a UDP socket to match the server's UDP implementation
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set socket timeout for receiving response
    client.settimeout(5.0)
    
    try:
        # Send an initial packet to the server to establish connection
        # The server will detect this as a new client and send back configuration
        connection_request = json.dumps({"type": "connect"}).encode()
        client.sendto(connection_request, (ip, port_num))
        
        # Update UI to show connection attempt
        errorLabel.config(text=f"Connecting to {ip}:{port_num}...")
        errorLabel.update()
        
        # Receive configuration from server
        # The server sends: {"screenWidth": 640, "screenHeight": 480, "pad": "left" or "right"}
        data, server_addr = client.recvfrom(4096)
        
        # Parse the JSON configuration received from server
        config = json.loads(data.decode())
        
        # Extract configuration values
        screenWidth = config.get("screenWidth", 640)
        screenHeight = config.get("screenHeight", 480)
        pad = config.get("pad", "left")
        
        # Validate received configuration
        if pad not in ["left", "right"]:
            errorLabel.config(text="Error: Invalid paddle assignment from server.")
            errorLabel.update()
            client.close()
            return
        
        # Update UI to show successful connection
        errorLabel.config(text=f"Connected! Assigned as {pad} player.")
        errorLabel.update()
        
        # Small delay to show success message
        app.after(500, lambda: None)
        
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
    
    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(screenWidth, screenHeight, pad, client)  # User will be either left or right paddle
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
