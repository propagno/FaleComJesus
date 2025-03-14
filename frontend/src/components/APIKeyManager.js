import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Button, 
  Card, 
  CardHeader, 
  CardContent, 
  Typography, 
  TextField, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  IconButton,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import apiKeyService from '../services/apiKeyService';

const PROVIDERS = [
  { id: 'openai', name: 'OpenAI' },
  { id: 'anthropic', name: 'Anthropic Claude' },
  { id: 'google', name: 'Google Gemini' },
  { id: 'mistral', name: 'Mistral AI' },
  { id: 'llama', name: 'Meta Llama' },
  { id: 'cohere', name: 'Cohere' },
  { id: 'other', name: 'Other' }
];

const APIKeyManager = () => {
  const { accessToken } = useAuth();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Form state
  const [provider, setProvider] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [formError, setFormError] = useState(null);
  
  // Confirmation dialog state
  const [openDialog, setOpenDialog] = useState(false);
  const [keyToDelete, setKeyToDelete] = useState(null);

  // Fetch API keys on component mount
  useEffect(() => {
    fetchApiKeys();
  }, [accessToken]);

  // Function to fetch API keys
  const fetchApiKeys = async () => {
    setLoading(true);
    try {
      const response = await apiKeyService.listApiKeys();
      setApiKeys(response.api_keys);
      setError(null);
    } catch (err) {
      console.error('Error fetching API keys:', err);
      setError('Failed to load API keys. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Function to add a new API key
  const handleAddKey = async (e) => {
    e.preventDefault();
    
    // Validate form fields
    if (!provider) {
      setFormError('Please select a provider');
      return;
    }
    
    if (!apiKey) {
      setFormError('Please enter an API key');
      return;
    }
    
    setLoading(true);
    setFormError(null);
    
    try {
      const response = await apiKeyService.addApiKey(provider, apiKey);
      
      // Show success message
      setSuccess(response.message);
      
      // Reset form
      setProvider('');
      setApiKey('');
      
      // Reload API keys
      fetchApiKeys();
    } catch (err) {
      console.error('Error adding API key:', err);
      setFormError(err.response?.data?.message || 'Failed to add API key. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Function to request API key deletion
  const confirmDelete = (key) => {
    setKeyToDelete(key);
    setOpenDialog(true);
  };
  
  // Function to cancel deletion
  const handleCancelDelete = () => {
    setOpenDialog(false);
    setKeyToDelete(null);
  };
  
  // Function to delete an API key
  const handleDeleteKey = async () => {
    if (!keyToDelete) return;
    
    setLoading(true);
    try {
      const response = await apiKeyService.deleteApiKey(keyToDelete.id);
      
      // Show success message
      setSuccess(response.message);
      
      // Reload API keys
      fetchApiKeys();
    } catch (err) {
      console.error('Error deleting API key:', err);
      setError('Failed to delete API key. Please try again later.');
    } finally {
      setLoading(false);
      setOpenDialog(false);
      setKeyToDelete(null);
    }
  };

  // Function to clear success message after delay
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        setSuccess(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [success]);

  // Function to get provider name from ID
  const getProviderName = (providerId) => {
    const provider = PROVIDERS.find(p => p.id === providerId);
    return provider ? provider.name : providerId;
  };

  return (
    <Card elevation={3}>
      <CardHeader 
        title="API Key Management" 
        subheader="Add, view, and delete your API keys"
      />
      
      <CardContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        
        <form onSubmit={handleAddKey}>
          <Typography variant="h6" gutterBottom>Add New API Key</Typography>
          
          <FormControl fullWidth margin="normal">
            <InputLabel id="provider-label">Provider</InputLabel>
            <Select
              labelId="provider-label"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              label="Provider"
              disabled={loading}
            >
              {PROVIDERS.map((provider) => (
                <MenuItem key={provider.id} value={provider.id}>
                  {provider.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            margin="normal"
            label="API Key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            disabled={loading}
            placeholder="Enter your API key"
          />
          
          {formError && (
            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
              {formError}
            </Typography>
          )}
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            startIcon={<AddIcon />}
            sx={{ mt: 2 }}
          >
            {loading ? 'Adding...' : 'Add API Key'}
          </Button>
        </form>
        
        <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>Your API Keys</Typography>
        
        {apiKeys.length === 0 ? (
          <Typography variant="body1" color="textSecondary">
            You haven't added any API keys yet.
          </Typography>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Provider</TableCell>
                  <TableCell>Added On</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {apiKeys.map((key) => (
                  <TableRow key={key.id}>
                    <TableCell>
                      <Typography variant="body1">
                        {getProviderName(key.provider)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {new Date(key.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={key.is_active ? "Active" : "Inactive"} 
                        color={key.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        color="error" 
                        onClick={() => confirmDelete(key)}
                        disabled={loading}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
      
      {/* Confirmation Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCancelDelete}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the API key for {keyToDelete && getProviderName(keyToDelete.provider)}? 
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteKey} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default APIKeyManager; 