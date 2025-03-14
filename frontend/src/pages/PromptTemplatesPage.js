import React from 'react';
import { Box, Typography, Container, Paper } from '@mui/material';
import PromptTemplateManager from '../components/PromptTemplateManager';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

const PromptTemplatesPage = () => {
  const { isAuthenticated } = useAuth();

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Gerenciar Templates de Prompt
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Crie e gerencie templates personalizados para melhorar suas interações com o assistente bíblico.
            Os templates permitem definir o tom, estilo e conteúdo das respostas.
          </Typography>
        </Box>
        
        <PromptTemplateManager />
      </Paper>
    </Container>
  );
};

export default PromptTemplatesPage; 