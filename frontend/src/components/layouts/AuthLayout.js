import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Box, Container, IconButton } from '@mui/material';
import { Brightness4 as DarkModeIcon, Brightness7 as LightModeIcon } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';

const AuthLayout = () => {
  const { isAuthenticated } = useAuth();
  const { mode, toggleTheme } = useTheme();
  
  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: (theme) => 
          mode === 'dark' 
            ? 'linear-gradient(to bottom, #1a237e 0%, #121212 100%)' 
            : 'linear-gradient(to bottom, #e8eaf6 0%, #c5cae9 100%)',
      }}
    >
      {/* Theme toggle button */}
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <IconButton 
          onClick={toggleTheme} 
          color={mode === 'dark' ? 'inherit' : 'primary'}
          sx={{ 
            bgcolor: mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
            '&:hover': {
              bgcolor: mode === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
            }
          }}
        >
          {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
        </IconButton>
      </Box>
      
      {/* Main content */}
      <Container component="main" maxWidth="lg" sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
        <Outlet />
      </Container>
      
      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          textAlign: 'center',
          color: mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)',
        }}
      >
        Fale Com Jesus © {new Date().getFullYear()}
      </Box>
    </Box>
  );
};

export default AuthLayout; 