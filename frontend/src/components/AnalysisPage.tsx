import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  LinearProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Timeline,
  Analytics,
  CheckCircle,
  Error,
  Refresh,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/api';
import { JobStatus } from '../types';

const steps = [
  {
    label: 'Document Upload',
    description: 'Files uploaded successfully',
    icon: <CloudUpload />,
  },
  {
    label: 'Text Extraction',
    description: 'Extracting text from documents using OCR',
    icon: <Description />,
  },
  {
    label: 'Document Analysis',
    description: 'AI agents analyzing document content',
    icon: <Analytics />,
  },
  {
    label: 'Event Timeline',
    description: 'Extracting chronological events',
    icon: <Timeline />,
  },
  {
    label: 'Legal Recommendations',
    description: 'Generating legal insights and recommendations',
    icon: <Analytics />,
  },
];

const AnalysisPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);

  const fetchJobStatus = async () => {
    if (!jobId) return;

    try {
      const status = await apiService.getJobStatus(jobId);
      setJobStatus(status);
      setError(null);

      // Update step based on current step
      const stepMap: { [key: string]: number } = {
        'uploaded': 0,
        'extracting': 1,
        'analyzing': 2,
        'timeline': 3,
        'recommendations': 4,
      };

      if (status.current_step && stepMap[status.current_step] !== undefined) {
        setActiveStep(stepMap[status.current_step]);
      }

      // If completed, navigate to results
      if (status.status === 'completed') {
        setTimeout(() => {
          navigate(`/results/${jobId}`);
        }, 2000);
      }

      // If failed, show error
      if (status.status === 'failed') {
        setError(status.error || 'Analysis failed');
        dispatch({ type: 'SET_ERROR', payload: status.error || 'Analysis failed' });
      }
    } catch (err) {
      console.error('Failed to fetch job status:', err);
      setError('Failed to fetch job status');
    }
  };

  useEffect(() => {
    if (!jobId) {
      navigate('/');
      return;
    }

    // Initial fetch
    fetchJobStatus();

    // Poll every 2 seconds while processing
    const interval = setInterval(() => {
      if (jobStatus?.status === 'processing') {
        fetchJobStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, jobStatus?.status]);

  const getStepStatus = (stepIndex: number) => {
    if (!jobStatus) return 'pending';
    
    if (jobStatus.status === 'failed') {
      return stepIndex <= activeStep ? 'error' : 'pending';
    }
    
    if (stepIndex < activeStep) return 'completed';
    if (stepIndex === activeStep) return 'active';
    return 'pending';
  };

  const getProgressValue = () => {
    if (!jobStatus) return 0;
    if (jobStatus.status === 'completed') return 100;
    if (jobStatus.status === 'failed') return 0;
    return jobStatus.progress || (activeStep / steps.length) * 100;
  };

  const handleRetry = () => {
    if (jobId) {
      // Restart analysis
      apiService.startAnalysis(jobId).then(() => {
        setError(null);
        fetchJobStatus();
      }).catch(err => {
        setError('Failed to restart analysis');
      });
    }
  };

  if (!jobId) {
    return (
      <Container maxWidth="md">
        <Alert severity="error">Invalid job ID</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom textAlign="center">
          Analyzing Documents
        </Typography>
        <Typography variant="body1" color="text.secondary" textAlign="center" mb={4}>
          Job ID: {jobId}
        </Typography>

        {/* Progress Section */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">
              Analysis Progress
            </Typography>
            <Chip
              label={jobStatus?.status || 'loading'}
              color={
                jobStatus?.status === 'completed' ? 'success' :
                jobStatus?.status === 'failed' ? 'error' :
                jobStatus?.status === 'processing' ? 'info' : 'default'
              }
              variant="outlined"
            />
          </Box>
          
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {Math.round(getProgressValue())}% Complete
            </Typography>
            <LinearProgress variant="determinate" value={getProgressValue()} />
          </Box>

          {jobStatus?.current_step && (
            <Typography variant="body2" color="text.secondary">
              Current step: {jobStatus.current_step}
            </Typography>
          )}
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 4 }}
            action={
              <Button
                color="inherit"
                size="small"
                onClick={handleRetry}
                startIcon={<Refresh />}
              >
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {/* Steps */}
        <Paper sx={{ p: 3 }}>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => {
              const status = getStepStatus(index);
              return (
                <Step key={step.label}>
                  <StepLabel
                    StepIconComponent={() => (
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          bgcolor:
                            status === 'completed' ? 'success.main' :
                            status === 'active' ? 'primary.main' :
                            status === 'error' ? 'error.main' : 'grey.300',
                          color: status === 'pending' ? 'text.secondary' : 'white',
                        }}
                      >
                        {status === 'completed' ? (
                          <CheckCircle />
                        ) : status === 'error' ? (
                          <Error />
                        ) : (
                          step.icon
                        )}
                      </Box>
                    )}
                  >
                    {step.label}
                  </StepLabel>
                  <StepContent>
                    <Typography color="text.secondary">
                      {step.description}
                    </Typography>
                  </StepContent>
                </Step>
              );
            })}
          </Stepper>
        </Paper>

        {/* Job Info */}
        {state.currentJob && (
          <Card sx={{ mt: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Uploaded Files
              </Typography>
              <List dense>
                {state.currentJob.files.map((file, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Description color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.filename}
                      secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <Box display="flex" justifyContent="space-between" mt={4}>
          <Button
            variant="outlined"
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
          {jobStatus?.status === 'completed' && (
            <Button
              variant="contained"
              onClick={() => navigate(`/results/${jobId}`)}
            >
              View Results
            </Button>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default AnalysisPage;
