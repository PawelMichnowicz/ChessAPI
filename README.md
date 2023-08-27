# Chess Game - Microservices Project

This repository contains three microservices for a chess game application, implemented as separate Dockerized services:
1. **Chess Game Server**
2. **Chess Game Client**
3. **Django Server (Chess Game Django Server)**

## Server (Chess Game Server)

The server is responsible for handling the game logic and maintaining the state of ongoing chess matches. 

## Client (Chess Game Client)

The client allows users to play chess in the terminal.

## Django Server (Chess Game Django Server)

The Django server is responsible for handling users authentication, managing challenges and game results. It uses GraphQL to expose API endpoints for interacting and managing user data.

## Usage and installation

1. Clone repository and build the Docker images and start the services:
```sh
git clone https://github.com/PawelMichnowicz/API-TransApp.git
docker-compose up --build
```

2. Run chess game client script
```sh
cd ChessAPI
python ./game_server/client.py
```
3. You can start game by input predefined users and challange instances
```sh
username_1 = player_1
username_2 = player_2
challange id = 12341234-1234-1234-1234-aaaaaaaaaaaa
```

