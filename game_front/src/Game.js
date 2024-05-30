// Game.js
import React, { useEffect, useState } from "react";
import Modal from "react-modal";
import { toast } from "react-toastify";
import Board from "./Board";
import Login from "./Login";
import WaitingForOpponent from './WaitingForOpponent';

function Game() {
  const [ws, setWs] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [gameState, setGameState] = useState([]);
  const [gameInfo, setGameInfo] = useState(null);
  const [waitingForOpponent, setWaitingForOpponent] = useState(false);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [drawOffered, setDrawOffered] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket("ws://localhost:5050");

    websocket.onopen = () => {
      console.log("Connected to the server");
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      switch (message.type) {
        case "game_state":
          setGameState(message.state);
          handleValidMove();
          break;
        case "waiting_for_opponent":
          setWaitingForOpponent(true);
          break;
        case "login_success":
          setIsLoggedIn(true);
          setWaitingForOpponent(false);
          break;
        case "opp_login_success":
          setWaitingForOpponent(false);
          break;
        case "game_info":
          setGameInfo(message.data);
          break;
        case "error":
          toast.error(message.content);
          break;
        case "draw_offer_received":
          setModalIsOpen(true);
          break;
        case "draw_rejected":
          toast.info("Draw rejected.");
          break;
        default:
          console.log("Unhandled message type:", message.type);
      }
    };

    websocket.onclose = () => console.log("Disconnected from the server");
    websocket.onerror = (error) => console.error("Connection error:", error);

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const handleLogin = (gameId, username) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "login", gameId, username }));
    }
  };

  const handleMove = (from, to) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "move", from, to }));
    }
  };

  const handleValidMove = () => {
    setDrawOffered(false);
    if (modalIsOpen) {
      setModalIsOpen(false);
      ws.send(JSON.stringify({ type: "reject_draw" }));
    }
  };

  const handleDrawOffer = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "offer_draw" }));
      setDrawOffered(true);
    }
  };

  const acceptDraw = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "accept_draw" }));
      setModalIsOpen(false);
    }
  };

  const rejectDraw = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "reject_draw" }));
      setModalIsOpen(false);
    }
  };

  const handleResign = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "resign" }));
    }
  };

  const handlePing = () => {
    console.log('Ping opponent button clicked');
  };

  const handleCancel = () => {
    console.log('Cancel button clicked');
  };

  return (
    <div>
      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <>
          {waitingForOpponent && (
            <WaitingForOpponent
              open={waitingForOpponent}
              onPing={handlePing}
              onCancel={handleCancel}
            />
          )}
          {gameInfo ? (
            <div>
              <p>
                Player: {gameInfo.username} [
                {gameInfo.is_white ? "White" : "Black"}]
              </p>
              <p>Opponent: {gameInfo.opponent_username}</p>
              <Board
                gameState={gameState}
                onMove={handleMove}
                isWhite={gameInfo.is_white}
              />
              <button
                className="button"
                onClick={handleDrawOffer}
                disabled={drawOffered}
              >
                Offer Draw
              </button>
              <button className="button resign-button" onClick={handleResign}>
                Resign
              </button>
            </div>
          ) : null}
          <Modal
            isOpen={modalIsOpen}
            onRequestClose={() => setModalIsOpen(false)}
            contentLabel="Draw Offer"
            ariaHideApp={false}
          >
            <h2>Draw Offer</h2>
            <button onClick={acceptDraw}>Accept</button>
            <button onClick={rejectDraw}>Reject</button>
          </Modal>
        </>
      )}
    </div>
  );
}

export default Game;
