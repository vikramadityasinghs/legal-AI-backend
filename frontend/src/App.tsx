import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Paper,
} from '@mui/material';
import { Gavel as GavelIcon } from '@mui/icons-material';

// Import components
import HomePage from './components/HomePage';
import UploadPage from './components/UploadPage';
import AnalysisPage from './components/AnalysisPage';
import ResultsPage from './components/ResultsPage';
import { AppProvider } from './context/AppContext';

const App: React.FC = () => {
  return (
    <AppProvider>
      <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
        {/* Header */}
        <AppBar position="static" elevation={1}>
          <Toolbar>
            <GavelIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              AI Legal Document Analysis
            </Typography>
            <Typography variant="subtitle2" color="inherit" sx={{ opacity: 0.8 }}>
              Indian Law Specialized
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ py: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/analysis/:jobId" element={<AnalysisPage />} />
            <Route path="/results/:jobId" element={<ResultsPage />} />
          </Routes>
        </Container>

        {/* Footer */}
        <Paper elevation={0} sx={{ mt: 8, py: 3, backgroundColor: 'primary.main', color: 'white' }}>
          <Container maxWidth="lg">
            <Typography variant="body2" align="center">
              © 2025 AI Legal Document Analysis System | Built for Indian Law | Multi-Agent AI
            </Typography>
          </Container>
        </Paper>
      </Box>
    </AppProvider>
  );
};

export default App;
