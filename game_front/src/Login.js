import React, { useState } from 'react';

function Login({ onLogin }) {
  const [gameId, setGameId] = useState('');
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(gameId, username);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Game ID"
          value={gameId}
          onChange={(e) => setGameId(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
