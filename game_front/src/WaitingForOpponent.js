import React from 'react';
import { Backdrop, Box, Button, Typography } from '@mui/material';
import './WaitingForOpponent.css'; 

function WaitingForOpponent({ open, onPing, onCancel }) {
  return (
    <Backdrop className="backdrop" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }} open={open}>
      <Box className="waiting-box">
        <Typography variant="h6" className="waiting-title">
          Waiting for the opponent<span className="dots"></span>
        </Typography>
        <Box className="waiting-buttons">
          <Button className="waiting-button-primary" variant="contained" onClick={onPing}>
            Ping Opponent
          </Button>
          <Button className="waiting-button-secondary" variant="outlined" onClick={onCancel}>
            Cancel
          </Button>
        </Box>
      </Box>
    </Backdrop>
  );
}

export default WaitingForOpponent;
