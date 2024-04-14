import React, { useState } from 'react'; // Dodaj import useState tutaj
import './Board.css';


const Board = ({ gameState, onMove, isWhite }) => {
  const [selectedSquare, setSelectedSquare] = useState(null);

  const getImageSrc = (piece) => {
    if (!piece) return null;
    return `/images/${piece}.png`;
  };


  // Zmodyfikowana funkcja, aby przekształcić indeksy w zależności od koloru
  const handleSquareClick = (rowIndex, colIndex) => {
    // Oblicz pozycję w notacji szachowej
    const rowChar = isWhite ? 8 - rowIndex : rowIndex + 1;
    const colChar = isWhite ? String.fromCharCode(97 + colIndex) : String.fromCharCode(104 - colIndex);
    const position = `${colChar}${rowChar}`;

    if (selectedSquare) {
      onMove(selectedSquare, position);
      setSelectedSquare(null);
    } else {
      setSelectedSquare(position);
    }
  };


  return (
    <div className="chessboard">
      {gameState.map((row, rowIndex) => (
        <div key={rowIndex} className="row">
          {row.map((piece, colIndex) => (
            <div key={colIndex}
                 className={`square ${((rowIndex + colIndex) % 2 === 0) ? 'light' : 'dark'}`}
                 onClick={() => handleSquareClick(rowIndex, colIndex)}
            >
              {piece && <img src={getImageSrc(piece)} alt={piece} className="chess-piece" />}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default Board;