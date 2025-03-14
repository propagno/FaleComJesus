import axios from './axios';

/**
 * Serviço para gerenciar conversas
 */
const conversationService = {
  /**
   * Listar todas as conversas do usuário
   * @returns {Promise} - Promise com a lista de conversas
   */
  listConversations: async () => {
    try {
      const response = await axios.get('/api/conversations');
      return response.data;
    } catch (error) {
      console.error('Error listing conversations:', error);
      throw error;
    }
  },
  
  /**
   * Obter uma conversa específica com suas mensagens
   * @param {number} conversationId - ID da conversa
   * @returns {Promise} - Promise com a conversa e suas mensagens
   */
  getConversation: async (conversationId) => {
    try {
      const response = await axios.get(`/api/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  },
  
  /**
   * Criar uma nova conversa
   * @param {string} title - Título da conversa
   * @returns {Promise} - Promise com a conversa criada
   */
  createConversation: async (title) => {
    try {
      const response = await axios.post('/api/conversations', { title });
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },
  
  /**
   * Atualizar o título de uma conversa
   * @param {number} conversationId - ID da conversa
   * @param {string} title - Novo título
   * @returns {Promise} - Promise com a conversa atualizada
   */
  updateConversation: async (conversationId, title) => {
    try {
      const response = await axios.put(`/api/conversations/${conversationId}`, { title });
      return response.data;
    } catch (error) {
      console.error('Error updating conversation:', error);
      throw error;
    }
  },
  
  /**
   * Excluir uma conversa
   * @param {number} conversationId - ID da conversa a ser excluída
   * @returns {Promise} - Promise com o resultado da operação
   */
  deleteConversation: async (conversationId) => {
    try {
      const response = await axios.delete(`/api/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },
  
  /**
   * Adicionar uma mensagem a uma conversa
   * @param {number} conversationId - ID da conversa
   * @param {string} content - Conteúdo da mensagem
   * @param {string} sender - Remetente ('user' ou 'bot')
   * @param {object} metadata - Metadados adicionais
   * @returns {Promise} - Promise com a mensagem criada
   */
  addMessage: async (conversationId, content, sender, metadata = {}) => {
    try {
      const response = await axios.post(`/api/conversations/${conversationId}/messages`, 
        { content, sender, metadata }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error adding message:', error);
      throw error;
    }
  },
  
  /**
   * Obter mensagens de uma conversa
   * @param {number} conversationId - ID da conversa
   * @returns {Promise} - Promise com as mensagens da conversa
   */
  getMessages: async (conversationId) => {
    try {
      const response = await axios.get(`/api/conversations/${conversationId}/messages`);
      return response.data;
    } catch (error) {
      console.error('Error getting messages:', error);
      throw error;
    }
  },
  
  /**
   * Exportar conversa como texto
   * @param {number} conversationId - ID da conversa
   * @returns {Promise<string>} - Texto formatado da conversa
   */
  exportConversation: async (conversationId) => {
    try {
      const conversation = await conversationService.getConversation(conversationId);
      if (!conversation) {
        throw new Error('Conversation not found');
      }
      
      // Formatar a conversa como texto
      let text = `# ${conversation.title}\n\n`;
      text += `Data: ${new Date(conversation.created_at).toLocaleString()}\n\n`;
      
      if (conversation.messages && conversation.messages.length > 0) {
        conversation.messages.forEach(message => {
          const sender = message.sender === 'user' ? 'Você' : 'Bot';
          text += `## ${sender} (${new Date(message.created_at).toLocaleTimeString()}):\n`;
          text += `${message.content}\n\n`;
        });
      } else {
        text += "Nenhuma mensagem encontrada.";
      }
      
      return text;
    } catch (error) {
      console.error('Error exporting conversation:', error);
      throw error;
    }
  }
};

export default conversationService; 