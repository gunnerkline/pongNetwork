# Pong

This project uses a UDP socket to achieve connections between two players, multiple spectators, and the Server

## Installation

This project requires the installation of the [pygame](https://www.pygame.org/docs/) library. This has already been stated in requirements, but if it's still uninstalled, use the package manager [pip](https://pip.pypa.io/en/stable/) to install pygame.

```bash
pip install pygame
```

## Usage

The Host's IP is: 127.0.0.1

The Port is: 62222

Input these values into the application window when prompted

## Key Notes

The first connected user is considered an "Authoritative" user and will send their own score and ball location to all other users.

The Q key at any time automatically closes the application.

Upon game over, the R key restarts the game for both players and can only be used by the players.

