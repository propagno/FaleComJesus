import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress,
  IconButton,
  Divider,
  Card,
  CardContent,
  Grid,
  Drawer,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { 
  Send as SendIcon, 
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon,
  Menu as MenuIcon,
  Edit as EditIcon,
  Add as AddIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from '../services/axios';
import LLMSelector from './LLMSelector';
import ConversationList from './ConversationList';
import conversationService from '../services/conversationService';
import PromptTemplateManager from './PromptTemplateManager';

const Chat = () => {
  const { accessToken, currentUser } = useAuth();
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [provider, setProvider] = useState(localStorage.getItem('selectedProvider') || 'openai');
  const [model, setModel] = useState(localStorage.getItem('selectedModel') || 'gpt-3.5-turbo');
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showTemplateDrawer, setShowTemplateDrawer] = useState(false);
  
  const messagesEndRef = useRef(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Scroll to bottom of chat when conversation updates
  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Load conversation when conversation ID changes
  useEffect(() => {
    if (currentConversationId && accessToken) {
      loadConversation(currentConversationId);
    } else {
      setConversation([]);
    }
  }, [currentConversationId, accessToken]);

  // Load conversation from the server
  const loadConversation = async (conversationId) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await conversationService.getConversation(conversationId);
      
      // Convert server messages to local format
      const messages = result.messages ? result.messages.map(msg => ({
        text: msg.content,
        sender: msg.sender,
        timestamp: msg.created_at,
        metadata: msg.metadata
      })) : [];
      
      setConversation(messages);
    } catch (err) {
      console.error('Error loading conversation:', err);
      setError('Failed to load conversation. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Handle provider change from LLM selector
  const handleProviderChange = (newProvider) => {
    setProvider(newProvider);
  };

  // Handle model change from LLM selector
  const handleModelChange = (newModel) => {
    setModel(newModel);
  };
  
  // Handle selecting a conversation from the list
  const handleSelectConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  // Handle template selection
  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setShowTemplateDrawer(false);
    // Could show a notification that template was selected
  };

  // Send message to backend
  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    if (!accessToken) {
      setError('Please log in to send messages');
      return;
    }
    
    // Add user message to conversation
    const userMessage = { 
      text: message, 
      sender: 'user', 
      timestamp: new Date().toISOString() 
    };
    setConversation(prev => [...prev, userMessage]);
    
    // Clear input field
    setMessage('');
    setError(null);
    setLoading(true);
    
    try {
      // Call chat API with selected provider and model
      const response = await axios.post('/api/chat/message', 
        { 
          message: userMessage.text,
          provider,
          model,
          conversation_id: currentConversationId,
          template_id: selectedTemplate ? selectedTemplate.id : null
        }
      );
      
      // If this is a new conversation, set the conversation ID
      if (!currentConversationId && response.data.conversation_id) {
        setCurrentConversationId(response.data.conversation_id);
      }
      
      // Add bot response to conversation
      const botMessage = {
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        provider,
        model
      };
      
      setConversation(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Show appropriate error message
      if (err.response?.status === 403) {
        setError('API key required. Please add a valid API key for this provider.');
      } else if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later.');
      } else {
        setError('Failed to get response. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Regenerate the last bot response
  const regenerateResponse = async () => {
    if (conversation.length === 0) return;
    
    // Find the last user message
    let lastUserMessageIndex = conversation.length - 1;
    while (lastUserMessageIndex >= 0 && conversation[lastUserMessageIndex].sender !== 'user') {
      lastUserMessageIndex--;
    }
    
    if (lastUserMessageIndex < 0) return;
    
    // Get the last user message
    const lastUserMessage = conversation[lastUserMessageIndex];
    
    // Remove messages after the last user message
    const newConversation = conversation.slice(0, lastUserMessageIndex + 1);
    setConversation(newConversation);
    
    // Send the last user message again
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/chat/message', 
        { 
          message: lastUserMessage.text,
          provider,
          model,
          regenerate: true,
          conversation_id: currentConversationId
        }
      );
      
      // Add regenerated bot response
      const botMessage = {
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        provider,
        model
      };
      
      setConversation(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error regenerating response:', err);
      setError('Failed to regenerate response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Copy message to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Could show a snackbar notification here
  };

  // Share message
  const shareMessage = (text) => {
    if (navigator.share) {
      navigator.share({
        title: 'Shared from Fale Com Jesus',
        text: text
      }).catch(err => console.error('Error sharing:', err));
    } else {
      // Fallback for browsers without Web Share API
      copyToClipboard(text);
      // Show a notification that it was copied instead
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      {/* Conversation List - Drawer on mobile, sidebar on desktop */}
      {isMobile ? (
        <>
          <IconButton
            color="primary"
            aria-label="open drawer"
            edge="start"
            onClick={() => setDrawerOpen(true)}
            sx={{ position: 'absolute', top: 16, left: 16, zIndex: 1 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Drawer
            anchor="left"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
          >
            <ConversationList 
              onSelectConversation={handleSelectConversation}
              selectedConversationId={currentConversationId}
            />
          </Drawer>
        </>
      ) : (
        <Box sx={{ width: 320, flexShrink: 0, borderRight: 1, borderColor: 'divider' }}>
          <ConversationList 
            onSelectConversation={handleSelectConversation}
            selectedConversationId={currentConversationId}
          />
        </Box>
      )}
      
      {/* Chat Area */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        flexGrow: 1, 
        p: 2,
        height: '100%',
        ...(isMobile && { width: '100%' })
      }}>
        {/* LLM Selector and Template Button */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <LLMSelector 
            onProviderChange={handleProviderChange}
            onModelChange={handleModelChange}
          />
          
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={() => setShowTemplateDrawer(true)}
            startIcon={selectedTemplate ? <EditIcon /> : <AddIcon />}
          >
            {selectedTemplate ? `Template: ${selectedTemplate.name}` : 'Select Template'}
          </Button>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {/* Chat Messages */}
        <Paper 
          elevation={2}
          sx={{ 
            p: 2, 
            flexGrow: 1, 
            mb: 2, 
            overflow: 'auto',
            maxHeight: 'calc(100vh - 250px)',
            bgcolor: 'background.default'
          }}
        >
          {conversation.length === 0 ? (
            <Box sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'text.secondary'
            }}>
              <Typography variant="h6" gutterBottom>
                Como posso ajudar você hoje?
              </Typography>
              <Typography variant="body1">
                Estou aqui para conversar e oferecer orientação baseada na Bíblia.
              </Typography>
            </Box>
          ) : (
            conversation.map((msg, index) => (
              <Box 
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Card
                  elevation={1}
                  sx={{
                    maxWidth: '80%',
                    bgcolor: msg.sender === 'user' ? 'primary.light' : 'background.paper',
                    color: msg.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                    borderRadius: 2
                  }}
                >
                  <CardContent sx={{ 
                    p: 2, 
                    '&:last-child': { pb: 2 },
                    position: 'relative'
                  }}>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {msg.text}
                    </Typography>
                    
                    {msg.sender === 'bot' && (
                      <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        mt: 2,
                        pt: 1,
                        borderTop: '1px solid',
                        borderColor: 'divider'
                      }}>
                        <Typography variant="caption" color="text.secondary">
                          {msg.provider || provider} / {msg.model || model}
                        </Typography>
                        
                        <Box>
                          <IconButton 
                            size="small" 
                            onClick={() => copyToClipboard(msg.text)}
                            title="Copy"
                            color="info"
                          >
                            <CopyIcon fontSize="small" />
                          </IconButton>
                          
                          <IconButton 
                            size="small" 
                            onClick={() => shareMessage(msg.text)}
                            title="Share"
                            color="info"
                          >
                            <ShareIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Box>
            ))
          )}
          <div ref={messagesEndRef} />
        </Paper>
        
        {/* Error Message */}
        {error && (
          <Typography color="error" variant="body2" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}
        
        {/* Input Area */}
        <Box 
          component="form" 
          sx={{ 
            display: 'flex',
            alignItems: 'flex-end'
          }}
          onSubmit={sendMessage}
        >
          <TextField
            fullWidth
            variant="outlined"
            label="Digite sua mensagem"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            multiline
            maxRows={4}
            disabled={loading || !accessToken}
            sx={{ mr: 1 }}
          />
          
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <Button
              variant="contained"
              color="primary"
              endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
              type="submit"
              disabled={loading || !message.trim() || !accessToken}
              sx={{ mb: 1 }}
            >
              {loading ? 'Enviando...' : 'Enviar'}
            </Button>
            
            {conversation.length > 0 && (
              <Button
                variant="outlined"
                color="secondary"
                startIcon={<RefreshIcon />}
                onClick={regenerateResponse}
                disabled={loading || !accessToken}
              >
                Regenerar
              </Button>
            )}
          </Box>
        </Box>
      </Box>
      
      {/* Template Manager Drawer */}
      <Drawer
        anchor="right"
        open={showTemplateDrawer}
        onClose={() => setShowTemplateDrawer(false)}
        sx={{ 
          width: 400,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 400,
            boxSizing: 'border-box',
            p: 2
          },
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Prompt Templates</Typography>
          <IconButton onClick={() => setShowTemplateDrawer(false)}>
            <CloseIcon />
          </IconButton>
        </Box>
        
        <PromptTemplateManager onSelectTemplate={handleSelectTemplate} />
      </Drawer>
    </Box>
  );
};

export default Chat; 