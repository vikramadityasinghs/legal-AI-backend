import React, { useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Delete,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/api';
import { UploadedFile } from '../types';

const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
    setUploadError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png'],
    },
    multiple: true,
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setUploadError('Please select at least one file to upload.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: Math.random() * 50 + 10 });
      }, 500);

      const response = await apiService.uploadDocuments(files);
      
      clearInterval(progressInterval);
      dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: 100 });

      // Create analysis job
      const uploadedFiles: UploadedFile[] = files.map(file => ({
        filename: file.name,
        size: file.size,
        type: file.type,
      }));

      const job = {
        job_id: response.job_id,
        files: uploadedFiles,
        status: 'uploaded' as const,
        created_at: new Date().toISOString(),
      };

      dispatch({ type: 'SET_CURRENT_JOB', payload: job });

      // Start analysis
      await apiService.startAnalysis(response.job_id);
      
      // Navigate to analysis page
      navigate(`/analysis/${response.job_id}`);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadError(error instanceof Error ? error.message : 'Upload failed. Please try again.');
      dispatch({ type: 'SET_ERROR', payload: 'Upload failed. Please try again.' });
    } finally {
      setUploading(false);
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom textAlign="center">
          Upload Legal Documents
        </Typography>
        <Typography variant="body1" color="text.secondary" textAlign="center" mb={4}>
          Upload your case files (PDFs, images) for AI-powered legal analysis
        </Typography>

        {/* Upload Area */}
        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            mb: 3,
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            bgcolor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'action.hover',
            },
          }}
        >
          <input {...getInputProps()} />
          <Box textAlign="center">
            <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
            </Typography>
            <Typography color="text.secondary" mb={2}>
              or click to browse files
            </Typography>
            <Button variant="outlined" component="span">
              Browse Files
            </Button>
            <Box mt={2}>
              <Chip label="PDF" size="small" sx={{ mr: 1 }} />
              <Chip label="JPG" size="small" sx={{ mr: 1 }} />
              <Chip label="PNG" size="small" />
            </Box>
          </Box>
        </Paper>

        {/* Selected Files */}
        {files.length > 0 && (
          <Paper sx={{ mb: 3 }}>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                Selected Files ({files.length})
              </Typography>
              <List dense>
                {files.map((file, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        onClick={() => removeFile(index)}
                        disabled={uploading}
                      >
                        <Delete />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      <Description color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={`${formatFileSize(file.size)} • ${file.type}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Paper>
        )}

        {/* Upload Progress */}
        {uploading && (
          <Box mb={3}>
            <Typography variant="body2" gutterBottom>
              Uploading files... {Math.round(state.uploadProgress)}%
            </Typography>
            <LinearProgress variant="determinate" value={state.uploadProgress} />
          </Box>
        )}

        {/* Error Alert */}
        {uploadError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {uploadError}
          </Alert>
        )}

        {/* Action Buttons */}
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Button
            variant="outlined"
            onClick={() => navigate('/')}
            disabled={uploading}
          >
            Back
          </Button>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            startIcon={uploading ? undefined : <CloudUpload />}
          >
            {uploading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
          </Button>
        </Box>

        {/* Instructions */}
        <Paper sx={{ mt: 4, p: 3, bgcolor: 'info.background' }}>
          <Typography variant="h6" gutterBottom color="info.main">
            Upload Guidelines
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Supported formats: PDF, JPG, PNG" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Maximum file size: 50MB per file" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Upload multiple documents for comprehensive analysis" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Error color="warning" fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Ensure documents are clear and readable for best results" />
            </ListItem>
          </List>
        </Paper>
      </Box>
    </Container>
  );
};

export default UploadPage;
