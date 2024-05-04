// Game.js
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Login from './Login';
import Board from './Board';

function Game() {
  const [ws, setWs] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [gameState, setGameState] = useState([]); 
  const [gameInfo, setGameInfo] = useState(null);
  const [waitingForOpponent, setWaitingForOpponent] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:5050');

    websocket.onopen = () => {
      console.log('Connected to the server');
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "game_state") {
        setGameState(message.state);
      } else if (message.type === "waiting_for_opponent") {
        setWaitingForOpponent(true);
      } else if (message.type === 'login_success') {
        setIsLoggedIn(true);
        setWaitingForOpponent(false); 
      } else if (message.type === "game_info") {
        setGameInfo(message.data);
      } else if (message.type === "error"){
        toast.error(message.content);
      }
    };

    websocket.onclose = () => console.log('Disconnected from the server');
    websocket.onerror = (error) => console.error('Connection error:', error);

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const handleLogin = (gameId, username) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'login', gameId, username }));
    }
  };

  const handleMove = (from, to) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'move', from, to }));
    }
  };

  return (
    <div>
      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <>
          {waitingForOpponent ? <p>Waiting for the opponent...</p> : null}
          {gameInfo ? (
            <div>
              <p>Player: {gameInfo.username} [{gameInfo.is_white ? "White" : "Black"}]</p>
              <p>Opponent: {gameInfo.opponent_username}</p>
              <Board gameState={gameState} onMove={handleMove} isWhite={gameInfo.is_white} />
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

export default Game;