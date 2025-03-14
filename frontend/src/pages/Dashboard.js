import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Typography, 
  Card, 
  CardContent, 
  CardHeader, 
  Divider,
  TextField,
  Button,
  Box,
  Paper,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import axios from '../services/axios';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [dailyMessage, setDailyMessage] = useState(null);
  const [recentNotes, setRecentNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [noteLoading, setNoteLoading] = useState(false);
  
  // Fetch daily message and recent notes
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch daily message
        const messageResponse = await axios.get('/api/v1/daily-messages/today');
        setDailyMessage(messageResponse.data);
        
        // Fetch recent notes
        const notesResponse = await axios.get('/api/v1/notes/recent');
        setRecentNotes(notesResponse.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  // Handle saving a new note
  const handleSaveNote = async () => {
    if (!newNote.trim()) return;
    
    setNoteLoading(true);
    try {
      const response = await axios.post('/api/v1/notes', {
        content: newNote,
        daily_message_id: dailyMessage?.id
      });
      
      // Add the new note to the recent notes
      setRecentNotes([response.data, ...recentNotes.slice(0, 1)]);
      setNewNote('');
    } catch (error) {
      console.error('Error saving note:', error);
    } finally {
      setNoteLoading(false);
    }
  };
  
  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Message */}
        <Grid item xs={12}>
          <Paper 
            elevation={0}
            sx={{ 
              p: 3, 
              display: 'flex', 
              flexDirection: 'column',
              background: 'linear-gradient(45deg, #3f51b5 30%, #5c6bc0 90%)',
              color: 'white',
              borderRadius: 2
            }}
          >
            <Typography variant="h4" gutterBottom>
              Bem-vindo, {currentUser?.first_name || 'Peregrino'}!
            </Typography>
            <Typography variant="body1">
              "Que a paz de Cristo esteja com você hoje e sempre."
            </Typography>
          </Paper>
        </Grid>
        
        {/* Daily Message */}
        <Grid item xs={12} md={7}>
          <Card sx={{ height: '100%' }}>
            <CardHeader 
              title="Mensagem do Dia" 
              sx={{ 
                bgcolor: 'primary.main', 
                color: 'primary.contrastText',
                pb: 1
              }}
            />
            <CardContent>
              {dailyMessage ? (
                <>
                  <Typography variant="body1" paragraph>
                    {dailyMessage.message}
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ bgcolor: 'background.default', p: 2, borderRadius: 1 }}>
                    <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                      "{dailyMessage.bible_verse}"
                    </Typography>
                    <Typography variant="subtitle2" sx={{ mt: 1, textAlign: 'right' }}>
                      — {dailyMessage.bible_reference}
                    </Typography>
                  </Box>
                </>
              ) : (
                <Typography variant="body1" color="text.secondary">
                  Não há mensagem disponível para hoje. Volte amanhã!
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Daily Reflection */}
        <Grid item xs={12} md={5}>
          <Card sx={{ height: '100%' }}>
            <CardHeader 
              title="Sua Reflexão" 
              sx={{ 
                bgcolor: 'secondary.main', 
                color: 'secondary.contrastText',
                pb: 1
              }}
            />
            <CardContent>
              <TextField
                fullWidth
                multiline
                rows={4}
                placeholder="Escreva sua reflexão sobre a mensagem de hoje..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <Button 
                variant="contained" 
                color="secondary"
                onClick={handleSaveNote}
                disabled={noteLoading || !newNote.trim()}
                fullWidth
              >
                {noteLoading ? <CircularProgress size={24} color="inherit" /> : 'Salvar Reflexão'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Notes */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Suas Reflexões Recentes" 
              sx={{ 
                bgcolor: 'primary.light', 
                color: 'primary.contrastText',
                pb: 1
              }}
            />
            <CardContent>
              {recentNotes.length > 0 ? (
                <Grid container spacing={2}>
                  {recentNotes.map((note) => (
                    <Grid item xs={12} md={6} key={note.id}>
                      <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          {new Date(note.created_at).toLocaleDateString('pt-BR', { 
                            weekday: 'long', 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric' 
                          })}
                        </Typography>
                        <Typography variant="body1">
                          {note.content}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body1" color="text.secondary" align="center">
                  Você ainda não tem reflexões. Comece escrevendo uma acima!
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 