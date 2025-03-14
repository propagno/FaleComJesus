import React, { useState, useEffect } from 'react';
import {
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Typography,
  Box,
  Tooltip,
  FormHelperText,
  IconButton
} from '@mui/material';
import { Info as InfoIcon, Settings as SettingsIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiKeyService from '../services/apiKeyService';

// List of available LLM providers
const PROVIDERS = [
  { id: 'openai', name: 'OpenAI', models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'] },
  { id: 'anthropic', name: 'Claude', models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'] },
  { id: 'google', name: 'Gemini', models: ['gemini-pro', 'gemini-ultra'] },
  { id: 'mistral', name: 'Mistral AI', models: ['mistral-tiny', 'mistral-small', 'mistral-large'] },
  { id: 'llama', name: 'Llama', models: ['llama-3'] },
  { id: 'cohere', name: 'Cohere', models: ['command', 'command-r', 'command-light'] }
];

const LLMSelector = ({ onProviderChange, onModelChange }) => {
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const [provider, setProvider] = useState(localStorage.getItem('selectedProvider') || 'openai');
  const [model, setModel] = useState(localStorage.getItem('selectedModel') || 'gpt-3.5-turbo');
  const [availableProviders, setAvailableProviders] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch user's API keys on component mount
  useEffect(() => {
    if (accessToken) {
      fetchAvailableProviders();
    }
  }, [accessToken]);

  // Fetch available providers (ones that the user has API keys for)
  const fetchAvailableProviders = async () => {
    setLoading(true);
    try {
      const response = await apiKeyService.listApiKeys();
      
      // Filter active API keys
      const activeKeys = response.api_keys.filter(key => key.is_active);
      
      // Map to provider IDs
      const providerIds = activeKeys.map(key => key.provider);
      
      // Update available providers
      setAvailableProviders(providerIds);
      
      // If current provider is not available, reset to default or first available
      if (providerIds.length > 0 && !providerIds.includes(provider)) {
        // Set to first available provider
        const newProvider = providerIds[0];
        handleProviderChange(newProvider);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching available providers:', err);
      setError('Failed to load available AI models');
    } finally {
      setLoading(false);
    }
  };

  // Handle provider change
  const handleProviderChange = (newProvider) => {
    setProvider(newProvider);
    localStorage.setItem('selectedProvider', newProvider);
    
    // Get default model for this provider
    const providerInfo = PROVIDERS.find(p => p.id === newProvider);
    const defaultModel = providerInfo?.models[0] || '';
    
    // Update model
    setModel(defaultModel);
    localStorage.setItem('selectedModel', defaultModel);
    
    // Notify parent components
    if (onProviderChange) {
      onProviderChange(newProvider);
    }
    
    if (onModelChange) {
      onModelChange(defaultModel);
    }
  };

  // Handle model change
  const handleModelChange = (newModel) => {
    setModel(newModel);
    localStorage.setItem('selectedModel', newModel);
    
    // Notify parent component
    if (onModelChange) {
      onModelChange(newModel);
    }
  };

  // Navigate to API keys management page
  const goToAPIKeySettings = () => {
    navigate('/profile');
  };

  // Get current provider info
  const currentProvider = PROVIDERS.find(p => p.id === provider) || PROVIDERS[0];
  
  // Get available models for current provider
  const availableModels = currentProvider.models;

  return (
    <Box sx={{ display: 'flex', alignItems: 'flex-start', flexDirection: 'column', mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
        <Typography variant="subtitle2" sx={{ mr: 1 }}>
          AI Model:
        </Typography>
        
        <Tooltip title="Go to API key settings">
          <IconButton 
            size="small" 
            color="primary" 
            onClick={goToAPIKeySettings}
            sx={{ ml: 'auto' }}
          >
            <SettingsIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
        <FormControl 
          size="small" 
          sx={{ mr: 2, minWidth: 120 }}
          error={Boolean(error)}
          disabled={loading || availableProviders.length === 0}
        >
          <InputLabel id="provider-select-label">Provider</InputLabel>
          <Select
            labelId="provider-select-label"
            value={provider}
            label="Provider"
            onChange={(e) => handleProviderChange(e.target.value)}
          >
            {PROVIDERS.map((p) => (
              <MenuItem 
                key={p.id} 
                value={p.id}
                disabled={!availableProviders.includes(p.id)}
              >
                {p.name}
              </MenuItem>
            ))}
          </Select>
          {error && <FormHelperText>{error}</FormHelperText>}
        </FormControl>
        
        <FormControl 
          size="small" 
          sx={{ minWidth: 140 }}
          disabled={loading || availableProviders.length === 0}
        >
          <InputLabel id="model-select-label">Model</InputLabel>
          <Select
            labelId="model-select-label"
            value={model}
            label="Model"
            onChange={(e) => handleModelChange(e.target.value)}
          >
            {availableModels.map((m) => (
              <MenuItem key={m} value={m}>
                {m}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Tooltip title="You'll need to add API keys for the providers you want to use">
          <IconButton size="small" color="info" sx={{ ml: 1 }}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      {availableProviders.length === 0 && (
        <Typography variant="body2" color="error" sx={{ mt: 1 }}>
          No API keys added. Please add keys in settings.
        </Typography>
      )}
    </Box>
  );
};

export default LLMSelector; 