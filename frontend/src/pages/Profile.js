import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Box, 
  Grid, 
  Divider, 
  Avatar,
  Card,
  CardContent,
  Alert,
  Snackbar,
  CircularProgress,
  Tab,
  Tabs
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import SettingsIcon from '@mui/icons-material/Settings';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import { useAuth } from '../contexts/AuthContext';
import APIKeyManager from '../components/APIKeyManager';

const Profile = () => {
  const { user, accessToken, updateUserProfile } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [openSnackbar, setOpenSnackbar] = useState(false);
  
  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setEmail(user.email || '');
    }
  }, [user]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        updateUserProfile(data.user);
        setMessage({ type: 'success', text: 'Perfil atualizado com sucesso!' });
        setOpenSnackbar(true);
      } else {
        const errorData = await response.json();
        setMessage({ type: 'error', text: errorData.message || 'Erro ao atualizar perfil' });
        setOpenSnackbar(true);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({ type: 'error', text: 'Erro de conexão. Tente novamente.' });
      setOpenSnackbar(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'As senhas não coincidem' });
      setOpenSnackbar(true);
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Senha alterada com sucesso!' });
        setOpenSnackbar(true);
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        const errorData = await response.json();
        setMessage({ type: 'error', text: errorData.message || 'Erro ao alterar senha' });
        setOpenSnackbar(true);
      }
    } catch (error) {
      console.error('Error changing password:', error);
      setMessage({ type: 'error', text: 'Erro de conexão. Tente novamente.' });
      setOpenSnackbar(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Meu Perfil
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          centered
          sx={{ mb: 3 }}
        >
          <Tab icon={<SettingsIcon />} label="Perfil" />
          <Tab icon={<VpnKeyIcon />} label="Chaves API" />
        </Tabs>
        
        {activeTab === 0 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Avatar 
                  sx={{ 
                    width: 120, 
                    height: 120, 
                    mb: 2,
                    fontSize: '3rem',
                    bgcolor: 'primary.main'
                  }}
                >
                  {firstName ? firstName.charAt(0).toUpperCase() : (email ? email.charAt(0).toUpperCase() : 'U')}
                </Avatar>
                
                <Typography variant="h6">
                  {firstName} {lastName}
                </Typography>
                
                <Typography variant="body2" color="textSecondary">
                  {email}
                </Typography>
                
                <Typography variant="caption" color="textSecondary" sx={{ mt: 2 }}>
                  Membro desde {user && user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={8}>
                <Box component="form" onSubmit={handleProfileUpdate} noValidate>
                  <Typography variant="h6" gutterBottom>
                    Informações Pessoais
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Nome"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Sobrenome"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="E-mail"
                        value={email}
                        disabled
                        margin="normal"
                      />
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button 
                      type="submit" 
                      variant="contained" 
                      color="primary"
                      startIcon={<SaveIcon />}
                      disabled={isLoading}
                    >
                      {isLoading ? <CircularProgress size={24} /> : 'Salvar Alterações'}
                    </Button>
                  </Box>
                </Box>
                
                <Divider sx={{ my: 3 }} />
                
                <Box component="form" onSubmit={handlePasswordChange} noValidate>
                  <Typography variant="h6" gutterBottom>
                    Alterar Senha
                  </Typography>
                  
                  <TextField
                    fullWidth
                    label="Senha Atual"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    margin="normal"
                    required
                  />
                  
                  <TextField
                    fullWidth
                    label="Nova Senha"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    margin="normal"
                    required
                    helperText="A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais"
                  />
                  
                  <TextField
                    fullWidth
                    label="Confirmar Nova Senha"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    margin="normal"
                    required
                    error={newPassword !== confirmPassword && confirmPassword !== ''}
                    helperText={newPassword !== confirmPassword && confirmPassword !== '' ? 'As senhas não coincidem' : ''}
                  />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button 
                      type="submit" 
                      variant="contained" 
                      color="primary"
                      disabled={isLoading || !currentPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword}
                    >
                      {isLoading ? <CircularProgress size={24} /> : 'Alterar Senha'}
                    </Button>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
        
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Gerenciar Chaves API
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Gerencie suas chaves API para utilizar diferentes provedores de modelos de linguagem no chat.
            </Typography>
            
            <APIKeyManager />
          </Box>
        )}
      </Paper>
      
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={message.type} 
          variant="filled"
        >
          {message.text}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Profile; 