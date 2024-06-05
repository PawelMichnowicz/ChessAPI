import React from "react";
import "./MoveHistory.css";

const pieceIcons = {
    "P-w": "",
    "N-w": "♘",
    "B-w": "♗",
    "R-w": "♖",
    "Q-w": "♕",
    "K-w": "♔",
    "P-b": "",
    "N-b": "♞",
    "B-b": "♝",
    "R-b": "♜",
    "Q-b": "♛",
    "K-b": "♚",
};

const MoveHistory = ({ history }) => {
    const renderMove = (move, index) => {
        if (!move) return null;

        const { from, to, piece, actions = [] } = move;
        const pieceIcon = pieceIcons[piece];

        let moveText = `${to}`;
        actions.forEach((action) => {
            switch (action) {
                case "capturing":
                    moveText = "x" + moveText;
                    if (piece.startsWith("P")) {
                        moveText = from[0] + moveText;
                    }
                    break;
                case "promotion":
                    moveText += "=H";
                    break;
                case "check":
                    moveText += "+";
                    break;
                case "castling":
                    moveText = to === "g1" || to === "g8" ? "O-O" : "O-O-O";
                    break;
                default:
                    break;
            }
        });
        return (
            <div key={index} className="move">
                <span className="piece-icon">{pieceIcon}</span>
                <span className="move-text">{moveText}</span>
            </div>
        );
    };

    const renderMovePair = (movePair, index) => (
        <div key={index} className="move-pair">
            <div className="move-number">{index + 1}.</div>
            <div className="white-move">{renderMove(movePair[0], index * 2)}</div>
            <div className="black-move">
                {movePair[1] && renderMove(movePair[1], index * 2 + 1)}
            </div>
        </div>
    );

    return (
        <div className="move-history">
            {Object.values(history).map(renderMovePair)}
        </div>
    );
};

export default MoveHistory;
