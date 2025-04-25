import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Box, Typography, Button } from '@mui/material';
import SectorInfo from './components/SectorInfo';
import logo from './assets/images/logo.jpg';

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/api/hello`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message));
  }, []);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route
          path="/"
          element={
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
                textAlign: 'center',
                backgroundColor: '#f5f5f5',
                padding: '2rem',
              }}
            >
              {/* Add an image above the title */}
              <Box
                component="img"
                src={logo} // Replace with your image URL
                alt="Sector Analytics Logo"
                sx={{
                  width: '33.33vw', // Sets width to one-third of the viewport width
                  height: 'auto',   // Maintains the aspect ratio
                  marginBottom: '1rem',
                }}
              />
              <Typography variant="h3" gutterBottom>
                Welcome to the Sector Analytics Platform
              </Typography>
              <Typography variant="h6" gutterBottom>
                {message || "Explore trends in scientific literature and market performance."}
              </Typography>
              <Button
                variant="contained"
                color="primary"
                size="large"
                component={Link}
                to="/sector-info"
                sx={{ marginTop: '2rem',
                  backgroundColor: '#ff6e6e91', // Custom background color (green)
                  color: '#fff', // Custom text color
                  '&:hover': {
                    backgroundColor: '#ff1c1c91', // Custom hover color
                  },
                }}
              >
                Explore Sector Data
              </Button>
            </Box>
          }
        />
        <Route path="/sector-info" element={<SectorInfo />} />
      </Routes>
    </Router>
  );
}

export default App;