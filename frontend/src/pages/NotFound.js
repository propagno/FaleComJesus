import React from 'react';
import { Container, Typography, Button, Box, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';

const NotFound = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 8, mb: 4, textAlign: 'center' }}>
      <Paper sx={{ p: 5, borderRadius: 2 }}>
        <Typography variant="h1" component="h1" gutterBottom sx={{ fontSize: '6rem', fontWeight: 'bold', color: 'primary.main' }}>
          404
        </Typography>
        
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 3 }}>
          Página Não Encontrada
        </Typography>
        
        <Typography variant="body1" color="textSecondary" paragraph sx={{ mb: 4 }}>
          A página que você está procurando parece não existir. Talvez o endereço esteja incorreto ou a página tenha sido movida.
        </Typography>
        
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center',
          alignItems: 'center',
          width: '100%',
          maxWidth: '400px',
          mx: 'auto',
          height: '200px',
          bgcolor: 'background.default',
          borderRadius: 2,
          mb: 4,
          p: 2
        }}>
          <Typography variant="h5" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
            "Vós sois a luz do mundo. Não se pode esconder uma cidade edificada sobre um monte."
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'right', fontWeight: 'bold' }}>
              - Mateus 5:14
            </Typography>
          </Typography>
        </Box>
        
        <Button
          component={RouterLink}
          to="/"
          variant="contained"
          color="primary"
          size="large"
          startIcon={<HomeIcon />}
        >
          Voltar para o Início
        </Button>
      </Paper>
    </Container>
  );
};

export default NotFound; 