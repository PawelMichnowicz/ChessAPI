import React, { useState } from "react";
import "./Board.css";

const Board = ({ gameState, onMove, isWhite }) => {
  const [selectedSquare, setSelectedSquare] = useState(null);

  const getImageSrc = (piece) => {
    if (!piece) return null;
    return `/images/${piece}.png`;
  };

  const handleSquareClick = (position) => {
    if (selectedSquare) {
      onMove(selectedSquare, position);
      setSelectedSquare(null);
    } else {
      setSelectedSquare(position);
    }
  };

  return (
    <div className="chessboard">
      {gameState.map((row, rowIndex) => {
        return (
          <div key={rowIndex} className="row">
            {row.map((piece, colIndex) => {
              // Transform indexes depending on the board orientation
              const rowChar = isWhite ? 8 - rowIndex : rowIndex + 1;
              const colChar = isWhite
                ? String.fromCharCode(97 + colIndex)
                : String.fromCharCode(104 - colIndex);
              const position = `${colChar}${rowChar}`;
              
              return (
                <div
                  key={colIndex}
                  className={`square ${
                    (rowIndex + colIndex) % 2 === 0 ? "light" : "dark"
                  } ${selectedSquare === position ? "selected" : ""}`}
                  onClick={() => handleSquareClick(position)}
                >
                  {piece && (
                    <img
                      src={getImageSrc(piece)}
                      alt={piece}
                      className="chess-piece"
                    />
                  )}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

export default Board;
