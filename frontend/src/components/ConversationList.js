import React, { useState, useEffect } from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Divider,
  Box,
  Button,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress,
  Alert,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  MoreVert as MoreVertIcon,
  Download as DownloadIcon,
  Menu as MenuIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import conversationService from '../services/conversationService';

const ConversationList = ({ onSelectConversation, selectedConversationId }) => {
  const { accessToken } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Estado para diálogos
  const [openNewDialog, setOpenNewDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [conversationTitle, setConversationTitle] = useState('');
  const [editingConversation, setEditingConversation] = useState(null);
  const [deletingConversation, setDeletingConversation] = useState(null);
  
  // Carregar conversas ao montar o componente
  useEffect(() => {
    if (accessToken) {
      fetchConversations();
    }
  }, [accessToken]);
  
  // Buscar conversas do usuário
  const fetchConversations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await conversationService.listConversations();
      setConversations(result.conversations || []);
    } catch (err) {
      console.error('Erro ao carregar conversas:', err);
      setError('Não foi possível carregar as conversas. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  // Abrir diálogo para criar nova conversa
  const handleOpenNewDialog = () => {
    setConversationTitle('Nova conversa');
    setOpenNewDialog(true);
  };
  
  // Abrir diálogo para editar conversa
  const handleOpenEditDialog = (conversation) => {
    setEditingConversation(conversation);
    setConversationTitle(conversation.title);
    setOpenEditDialog(true);
  };
  
  // Abrir diálogo para excluir conversa
  const handleOpenDeleteDialog = (conversation) => {
    setDeletingConversation(conversation);
    setOpenDeleteDialog(true);
  };
  
  // Fechar todos os diálogos
  const handleCloseDialogs = () => {
    setOpenNewDialog(false);
    setOpenEditDialog(false);
    setOpenDeleteDialog(false);
    setConversationTitle('');
    setEditingConversation(null);
    setDeletingConversation(null);
  };
  
  // Criar nova conversa
  const handleCreateConversation = async () => {
    try {
      setLoading(true);
      const result = await conversationService.createConversation(conversationTitle);
      
      // Adicionar nova conversa à lista
      setConversations(prev => [result.conversation, ...prev]);
      
      // Selecionar a nova conversa
      if (onSelectConversation && result.conversation) {
        onSelectConversation(result.conversation.id);
      }
      
      handleCloseDialogs();
    } catch (err) {
      console.error('Erro ao criar conversa:', err);
      setError('Não foi possível criar a conversa. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  // Atualizar título da conversa
  const handleUpdateConversation = async () => {
    if (!editingConversation) return;
    
    try {
      setLoading(true);
      const result = await conversationService.updateConversation(
        editingConversation.id, 
        conversationTitle
      );
      
      // Atualizar conversa na lista
      setConversations(prev => prev.map(conv => 
        conv.id === editingConversation.id 
          ? { ...conv, title: conversationTitle }
          : conv
      ));
      
      handleCloseDialogs();
    } catch (err) {
      console.error('Erro ao atualizar conversa:', err);
      setError('Não foi possível atualizar a conversa. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  // Excluir conversa
  const handleDeleteConversation = async () => {
    if (!deletingConversation) return;
    
    try {
      setLoading(true);
      await conversationService.deleteConversation(deletingConversation.id);
      
      // Remover conversa da lista
      setConversations(prev => prev.filter(conv => conv.id !== deletingConversation.id));
      
      // Se a conversa excluída estava selecionada, desselecionar
      if (onSelectConversation && selectedConversationId === deletingConversation.id) {
        onSelectConversation(null);
      }
      
      handleCloseDialogs();
    } catch (err) {
      console.error('Erro ao excluir conversa:', err);
      setError('Não foi possível excluir a conversa. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  // Exportar conversa como texto
  const handleExportConversation = async (conversation) => {
    try {
      setLoading(true);
      const text = await conversationService.exportConversation(conversation.id);
      
      // Criar um blob e link para download
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${conversation.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro ao exportar conversa:', err);
      setError('Não foi possível exportar a conversa. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        p: 2 
      }}>
        <Typography variant="h6" component="div">
          Minhas Conversas
        </Typography>
        <Button
          size="small"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenNewDialog}
          disabled={loading}
        >
          Nova
        </Button>
      </Box>
      
      <Divider />
      
      {error && (
        <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>
      )}
      
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      )}
      
      {conversations.length === 0 && !loading ? (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <Typography color="textSecondary">
            Nenhuma conversa encontrada
          </Typography>
        </Box>
      ) : (
        <List>
          {conversations.map((conversation) => (
            <ListItem
              key={conversation.id}
              button
              selected={selectedConversationId === conversation.id}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <ListItemText
                primary={conversation.title}
                secondary={new Date(conversation.updated_at).toLocaleDateString()}
              />
              <ListItemSecondaryAction>
                <Tooltip title="Exportar conversa">
                  <IconButton 
                    edge="end" 
                    aria-label="export"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExportConversation(conversation);
                    }}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Editar título">
                  <IconButton 
                    edge="end" 
                    aria-label="edit"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenEditDialog(conversation);
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Excluir conversa">
                  <IconButton 
                    edge="end" 
                    aria-label="delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenDeleteDialog(conversation);
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
      
      {/* Diálogo para criar nova conversa */}
      <Dialog open={openNewDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Nova Conversa</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Digite um título para sua nova conversa:
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Título da conversa"
            fullWidth
            value={conversationTitle}
            onChange={(e) => setConversationTitle(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs} color="primary">
            Cancelar
          </Button>
          <Button onClick={handleCreateConversation} color="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Diálogo para editar conversa */}
      <Dialog open={openEditDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Editar Conversa</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Edite o título da conversa:
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Título da conversa"
            fullWidth
            value={conversationTitle}
            onChange={(e) => setConversationTitle(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs} color="primary">
            Cancelar
          </Button>
          <Button onClick={handleUpdateConversation} color="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Atualizar'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Diálogo para excluir conversa */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDialogs}>
        <DialogTitle>Excluir Conversa</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Tem certeza que deseja excluir a conversa "{deletingConversation?.title}"? 
            Esta ação não pode ser desfeita.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs} color="primary">
            Cancelar
          </Button>
          <Button onClick={handleDeleteConversation} color="error" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Excluir'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConversationList; 