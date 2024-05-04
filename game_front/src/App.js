import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';
import Game from './Game';

function App() {
  return (
    <div className="App">
      <Game />
      <ToastContainer />
    </div>
  );
}

export default App;
