import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Paper,
  Divider
} from '@mui/material';
import { Helmet } from 'react-helmet';
import { useAuth } from '../contexts/AuthContext';
import APIKeyManager from '../components/APIKeyManager';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ProfilePage = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth="lg">
      <Helmet>
        <title>Perfil - Fale Com Jesus</title>
      </Helmet>
      
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Perfil
        </Typography>
        
        <Paper elevation={3} sx={{ mt: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Informações Pessoais" />
            <Tab label="API Keys" />
            <Tab label="Configurações" />
          </Tabs>
          
          <Divider />
          
          <TabPanel value={tabValue} index={0}>
            <Box>
              <Typography variant="h6">Informações da Conta</Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body1">
                  <strong>Email:</strong> {user?.email}
                </Typography>
                <Typography variant="body1">
                  <strong>Nome:</strong> {user?.first_name} {user?.last_name}
                </Typography>
                <Typography variant="body1">
                  <strong>Membro desde:</strong> {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </Typography>
                <Typography variant="body1">
                  <strong>Último acesso:</strong> {user?.last_login ? new Date(user.last_login).toLocaleDateString() : 'N/A'}
                </Typography>
              </Box>
            </Box>
          </TabPanel>
          
          <TabPanel value={tabValue} index={1}>
            <APIKeyManager />
          </TabPanel>
          
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6">Preferências</Typography>
            <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
              Em breve você poderá personalizar suas preferências aqui.
            </Typography>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default ProfilePage; 