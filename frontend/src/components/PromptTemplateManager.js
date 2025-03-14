import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Paper,
  Divider,
  Tooltip,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import promptTemplateService from '../services/promptTemplateService';

const PromptTemplateManager = ({ onSelectTemplate }) => {
  const { accessToken, currentUser } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  
  const [currentTemplate, setCurrentTemplate] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template: ''
  });

  // Load templates
  useEffect(() => {
    if (accessToken) {
      fetchTemplates();
    }
  }, [accessToken]);

  const fetchTemplates = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await promptTemplateService.getTemplates(accessToken);
      setTemplates(result.templates || []);
    } catch (err) {
      console.error('Error fetching templates:', err);
      setError('Failed to load templates. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Open create dialog
  const handleOpenCreateDialog = () => {
    setFormData({
      name: '',
      description: '',
      template: ''
    });
    setOpenCreateDialog(true);
  };

  // Close create dialog
  const handleCloseCreateDialog = () => {
    setOpenCreateDialog(false);
  };

  // Submit create form
  const handleCreateTemplate = async () => {
    setError(null);
    
    try {
      await promptTemplateService.createTemplate(formData, accessToken);
      setOpenCreateDialog(false);
      fetchTemplates();
    } catch (err) {
      console.error('Error creating template:', err);
      setError('Failed to create template. Please check your input and try again.');
    }
  };

  // Open edit dialog
  const handleOpenEditDialog = (template) => {
    setCurrentTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      template: template.template
    });
    setOpenEditDialog(true);
  };

  // Close edit dialog
  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
  };

  // Submit edit form
  const handleUpdateTemplate = async () => {
    if (!currentTemplate) return;
    
    setError(null);
    
    try {
      await promptTemplateService.updateTemplate(currentTemplate.id, formData, accessToken);
      setOpenEditDialog(false);
      fetchTemplates();
    } catch (err) {
      console.error('Error updating template:', err);
      setError('Failed to update template. Please check your input and try again.');
    }
  };

  // Open delete dialog
  const handleOpenDeleteDialog = (template) => {
    setCurrentTemplate(template);
    setOpenDeleteDialog(true);
  };

  // Close delete dialog
  const handleCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
  };

  // Confirm delete
  const handleDeleteTemplate = async () => {
    if (!currentTemplate) return;
    
    setError(null);
    
    try {
      await promptTemplateService.deleteTemplate(currentTemplate.id, accessToken);
      setOpenDeleteDialog(false);
      fetchTemplates();
    } catch (err) {
      console.error('Error deleting template:', err);
      setError('Failed to delete template. Please try again later.');
    }
  };

  // Select a template
  const handleSelectTemplate = (template) => {
    if (onSelectTemplate) {
      onSelectTemplate(template);
    }
  };

  // Render loading state
  if (loading && templates.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Prompt Templates</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          New Template
        </Button>
      </Box>

      {error && (
        <Typography color="error" variant="body2" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Paper sx={{ mb: 2 }}>
        <List>
          {templates.length === 0 ? (
            <ListItem>
              <ListItemText primary="No templates found. Create your first template!" />
            </ListItem>
          ) : (
            templates.map((template) => (
              <React.Fragment key={template.id}>
                <ListItem 
                  button 
                  onClick={() => handleSelectTemplate(template)}
                >
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {template.name}
                        {template.is_system && (
                          <Chip 
                            size="small" 
                            label="System" 
                            color="primary" 
                            sx={{ ml: 1 }}
                          />
                        )}
                      </Box>
                    }
                    secondary={template.description || 'No description'}
                  />
                  
                  {!template.is_system && (
                    <ListItemSecondaryAction>
                      <Tooltip title="Edit">
                        <IconButton 
                          edge="end" 
                          aria-label="edit"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenEditDialog(template);
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Delete">
                        <IconButton 
                          edge="end" 
                          aria-label="delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenDeleteDialog(template);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  )}
                </ListItem>
                <Divider />
              </React.Fragment>
            ))
          )}
        </List>
      </Paper>

      {/* Create Dialog */}
      <Dialog open={openCreateDialog} onClose={handleCloseCreateDialog} fullWidth maxWidth="md">
        <DialogTitle>Create New Template</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Name"
            type="text"
            fullWidth
            value={formData.name}
            onChange={handleChange}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            value={formData.description}
            onChange={handleChange}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            name="template"
            label="Template"
            multiline
            rows={10}
            fullWidth
            value={formData.template}
            onChange={handleChange}
            helperText="Use {message} to include the user's message. You can also use variables like {conversation_history} if available."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button onClick={handleCreateTemplate} variant="contained" startIcon={<SaveIcon />}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={openEditDialog} onClose={handleCloseEditDialog} fullWidth maxWidth="md">
        <DialogTitle>Edit Template</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Name"
            type="text"
            fullWidth
            value={formData.name}
            onChange={handleChange}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            value={formData.description}
            onChange={handleChange}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            name="template"
            label="Template"
            multiline
            rows={10}
            fullWidth
            value={formData.template}
            onChange={handleChange}
            helperText="Use {message} to include the user's message. You can also use variables like {conversation_history} if available."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button onClick={handleUpdateTemplate} variant="contained" startIcon={<SaveIcon />}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Delete Template</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this template? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteTemplate} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PromptTemplateManager; 