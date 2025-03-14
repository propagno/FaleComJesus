import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  IconButton,
  Divider
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import SaveIcon from '@mui/icons-material/Save';
import axios from '../services/axios';

const Notes = () => {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/v1/notes');
      setNotes(response.data || []);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsLoading(true);
    
    try {
      if (editingNoteId) {
        // Update existing note
        const response = await axios.put(`/api/v1/notes/${editingNoteId}`, { 
          title, 
          content 
        });
        
        if (response.status === 200) {
          fetchNotes();
          resetForm();
        }
      } else {
        // Create new note
        const response = await axios.post('/api/v1/notes', { 
          title, 
          content 
        });
        
        if (response.status === 201 || response.status === 200) {
          fetchNotes();
          resetForm();
        }
      }
    } catch (error) {
      console.error('Error saving note:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (note) => {
    setEditingNoteId(note.id);
    setTitle(note.title || '');
    setContent(note.content || '');
  };

  const handleDelete = async (id) => {
    try {
      const response = await axios.delete(`/api/v1/notes/${id}`);
      
      if (response.status === 200 || response.status === 204) {
        fetchNotes();
      }
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  const toggleFavorite = async (note) => {
    try {
      const response = await axios.put(`/api/v1/notes/${note.id}`, { 
        is_favorite: !note.is_favorite,
        title: note.title,
        content: note.content
      });
      
      if (response.status === 200) {
        fetchNotes();
      }
    } catch (error) {
      console.error('Error updating favorite status:', error);
    }
  };

  const resetForm = () => {
    setTitle('');
    setContent('');
    setEditingNoteId(null);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Minhas Anotações
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <TextField
            label="Título"
            variant="outlined"
            fullWidth
            margin="normal"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <TextField
            label="Conteúdo"
            variant="outlined"
            fullWidth
            multiline
            rows={4}
            margin="normal"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            {editingNoteId && (
              <Button 
                sx={{ mr: 2 }}
                onClick={resetForm}
              >
                Cancelar
              </Button>
            )}
            <Button 
              type="submit" 
              variant="contained" 
              disabled={isLoading || !content.trim()}
              startIcon={<SaveIcon />}
            >
              {editingNoteId ? 'Atualizar' : 'Salvar'} Anotação
            </Button>
          </Box>
        </Box>
      </Paper>
      
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Anotações Salvas
      </Typography>
      
      {notes.length === 0 ? (
        <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
          Você ainda não tem anotações. Crie sua primeira anotação acima.
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {notes.map((note) => (
            <Grid item xs={12} md={6} key={note.id}>
              <Card>
                <CardContent>
                  {note.title && (
                    <>
                      <Typography variant="h6" component="h2">
                        {note.title}
                      </Typography>
                      <Divider sx={{ my: 1 }} />
                    </>
                  )}
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {note.content}
                  </Typography>
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                    {new Date(note.created_at).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </Typography>
                </CardContent>
                <CardActions>
                  <IconButton onClick={() => toggleFavorite(note)} color={note.is_favorite ? "warning" : "default"}>
                    {note.is_favorite ? <StarIcon /> : <StarBorderIcon />}
                  </IconButton>
                  <IconButton onClick={() => handleEdit(note)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(note.id)}>
                    <DeleteIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default Notes; 