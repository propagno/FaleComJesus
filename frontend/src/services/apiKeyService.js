import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Serviço para gerenciar as operações de API Keys
 */
const apiKeyService = {
  /**
   * Lista todas as API Keys do usuário
   * @returns {Promise} - Promise com a lista de API Keys
   */
  listApiKeys: async () => {
    try {
      // Obtém o token do localStorage
      const accessToken = localStorage.getItem('accessToken');
      
      if (!accessToken) {
        throw new Error('No token available');
      }
      
      const response = await axios.get(`${API_URL}/api/keys`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error listing API keys:', error);
      throw error;
    }
  },
  
  /**
   * Adiciona uma nova API Key
   * @param {string} provider - Provedor da API Key
   * @param {string} apiKey - Valor da API Key
   * @returns {Promise} - Promise com o resultado da operação
   */
  addApiKey: async (provider, apiKey) => {
    try {
      // Obtém o token do localStorage
      const accessToken = localStorage.getItem('accessToken');
      
      if (!accessToken) {
        throw new Error('No token available');
      }
      
      const response = await axios.post(`${API_URL}/api/keys`, 
        { provider, api_key: apiKey },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error adding API key:', error);
      throw error;
    }
  },
  
  /**
   * Remove uma API Key
   * @param {number} id - ID da API Key a ser removida
   * @returns {Promise} - Promise com o resultado da operação
   */
  deleteApiKey: async (id) => {
    try {
      // Obtém o token do localStorage
      const accessToken = localStorage.getItem('accessToken');
      
      if (!accessToken) {
        throw new Error('No token available');
      }
      
      const response = await axios.delete(`${API_URL}/api/keys`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        data: { id }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error deleting API key:', error);
      throw error;
    }
  }
};

export default apiKeyService; 