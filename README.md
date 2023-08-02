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

The Django server is responsible for handling user authentication and managing challenges and game results. It uses GraphQL to expose API endpoints for interacting with the client and managing user data.

## How to Run

To run the entire application, you need to have Docker and Docker Compose installed on your system.

1. Clone this repository:
git clone https://github.com/your-username/chess-game.git

2. Build the Docker images and start the services:
docker-compose up --build


