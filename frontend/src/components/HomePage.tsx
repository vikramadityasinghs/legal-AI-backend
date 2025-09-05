import React from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Timeline,
  Gavel,
  CheckCircle,
  Speed,
  Security,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Description />,
      title: 'Document Analysis',
      description: 'AI-powered extraction and analysis of legal documents including PDFs and images',
    },
    {
      icon: <Timeline />,
      title: 'Event Timeline',
      description: 'Automated chronological timeline generation with party-specific roles',
    },
    {
      icon: <Gavel />,
      title: 'Legal Recommendations',
      description: 'Expert-level legal analysis and actionable recommendations',
    },
  ];

  const capabilities = [
    'Multi-format document support (PDF, JPG, PNG)',
    'Intelligent text extraction using OCR',
    'Party identification and role mapping',
    'Legal event chronology',
    'Case strength assessment',
    'Actionable next steps',
    'Comprehensive reporting',
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 6 }}>
        {/* Hero Section */}
        <Box textAlign="center" mb={6}>
          <Typography variant="h2" component="h1" gutterBottom color="primary">
            Legal Document AI Analyzer
          </Typography>
          <Typography variant="h5" color="text.secondary" mb={4}>
            Advanced AI-powered analysis for Indian legal documents
          </Typography>
          <Chip
            label="Production Ready"
            color="success"
            variant="outlined"
            sx={{ mr: 2 }}
          />
          <Chip
            label="Multi-Agent Pipeline"
            color="info"
            variant="outlined"
            sx={{ mr: 2 }}
          />
          <Chip
            label="Indian Law Specialized"
            color="warning"
            variant="outlined"
          />
        </Box>

        {/* Action Button */}
        <Box textAlign="center" mb={8}>
          <Button
            variant="contained"
            size="large"
            startIcon={<CloudUpload />}
            onClick={() => navigate('/upload')}
            sx={{ px: 6, py: 2, fontSize: '1.2rem' }}
          >
            Start Analysis
          </Button>
        </Box>

        {/* Features Grid */}
        <Grid container spacing={4} mb={6}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Box sx={{ mr: 2, color: 'primary.main' }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" component="h3">
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Capabilities Section */}
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h5" gutterBottom color="primary">
                  System Capabilities
                </Typography>
                <List dense>
                  {capabilities.map((capability, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircle color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={capability} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h5" gutterBottom color="primary">
                  Why Choose Our Platform?
                </Typography>
                <Box mb={3}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Speed color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Fast Processing</Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Multi-threaded AI pipeline for rapid document analysis
                  </Typography>
                </Box>

                <Box mb={3}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Security color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Secure & Private</Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Enterprise-grade security with local processing options
                  </Typography>
                </Box>

                <Box>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Gavel color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Expert Analysis</Typography>
                  </Box>
                  <Typography color="text.secondary">
                    Specialized for Indian legal system with comprehensive insights
                  </Typography>
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/upload')}
                  fullWidth
                >
                  Get Started Now
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage;
