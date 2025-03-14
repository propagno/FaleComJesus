import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import Chat from '../components/Chat';

const ChatPage = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Fale Com Jesus
      </Typography>
      
      <Box sx={{ height: 'calc(100vh - 200px)' }}>
        <Chat />
      </Box>
    </Container>
  );
};

export default ChatPage; 