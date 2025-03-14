import axios from './axios';

const promptTemplateService = {
  /**
   * Get all prompt templates available to the user
   * @param {string} accessToken - User access token
   * @returns {Promise<{templates: Array, count: number}>} - List of templates and count
   */
  getTemplates: async (accessToken) => {
    try {
      const response = await axios.get('/api/prompts', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting prompt templates:', error);
      throw error;
    }
  },

  /**
   * Get a specific prompt template by ID
   * @param {number} templateId - Template ID
   * @param {string} accessToken - User access token
   * @returns {Promise<Object>} - Template details
   */
  getTemplate: async (templateId, accessToken) => {
    try {
      const response = await axios.get(`/api/prompts/${templateId}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error getting prompt template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new prompt template
   * @param {Object} template - Template data (name, description, template)
   * @param {string} accessToken - User access token
   * @returns {Promise<Object>} - Created template
   */
  createTemplate: async (template, accessToken) => {
    try {
      const response = await axios.post('/api/prompts', template, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error creating prompt template:', error);
      throw error;
    }
  },

  /**
   * Update an existing prompt template
   * @param {number} templateId - Template ID
   * @param {Object} template - Updated template data
   * @param {string} accessToken - User access token
   * @returns {Promise<Object>} - Updated template
   */
  updateTemplate: async (templateId, template, accessToken) => {
    try {
      const response = await axios.put(`/api/prompts/${templateId}`, template, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error updating prompt template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a prompt template
   * @param {number} templateId - Template ID
   * @param {string} accessToken - User access token
   * @returns {Promise<{message: string}>} - Success message
   */
  deleteTemplate: async (templateId, accessToken) => {
    try {
      const response = await axios.delete(`/api/prompts/${templateId}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error deleting prompt template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Create a system template (admin only)
   * @param {Object} template - Template data
   * @param {string} accessToken - Admin access token
   * @returns {Promise<Object>} - Created template
   */
  createSystemTemplate: async (template, accessToken) => {
    try {
      const response = await axios.post('/api/prompts/system', template, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error creating system template:', error);
      throw error;
    }
  }
};

export default promptTemplateService; 