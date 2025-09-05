import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  Download,
  Timeline,
  Gavel,
  Assessment,
  Event,
  People,
  Description,
  Share,
  Print,
  Delete,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/api';
import { AnalysisResults } from '../types';

const ResultsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportDialog, setExportDialog] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!jobId) {
      navigate('/');
      return;
    }

    fetchResults();
  }, [jobId]);

  const fetchResults = async () => {
    if (!jobId) return;

    try {
      setLoading(true);
      const analysisResults = await apiService.getAnalysisResults(jobId);
      setResults(analysisResults);
      dispatch({ type: 'SET_RESULTS', payload: analysisResults });
      setError(null);
    } catch (err) {
      console.error('Failed to fetch results:', err);
      setError('Failed to load analysis results');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'excel' | 'json' | 'pdf') => {
    if (!jobId) return;

    try {
      setExporting(true);
      const blob = await apiService.exportResults(jobId, format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `legal-analysis-${jobId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setExportDialog(false);
    } catch (err) {
      console.error('Export failed:', err);
      setError('Export failed');
    } finally {
      setExporting(false);
    }
  };

  const handleDelete = async () => {
    if (!jobId) return;

    try {
      await apiService.deleteJob(jobId);
      navigate('/');
    } catch (err) {
      console.error('Delete failed:', err);
      setError('Failed to delete job');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStrengthColor = (strength: string) => {
    switch (strength.toLowerCase()) {
      case 'strong': return 'success';
      case 'moderate': return 'warning';
      case 'weak': return 'error';
      default: return 'default';
    }
  };

  if (!jobId) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error">Invalid job ID</Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Typography variant="h5">Loading results...</Typography>
        </Box>
      </Container>
    );
  }

  if (error || !results) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={fetchResults}>
              Retry
            </Button>
          }>
            {error || 'No results available'}
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Legal Analysis Results
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Job ID: {jobId} • Completed: {new Date(results.completed_at).toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Tooltip title="Export Results">
              <IconButton onClick={() => setExportDialog(true)} color="primary">
                <Download />
              </IconButton>
            </Tooltip>
            <Tooltip title="Print">
              <IconButton onClick={() => window.print()} color="primary">
                <Print />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Job">
              <IconButton onClick={handleDelete} color="error">
                <Delete />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Description color="primary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h6">
                      {results.extraction_stats.total_files}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Documents
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Event color="primary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h6">
                      {results.events.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Events Extracted
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Gavel color="primary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h6">
                      {results.recommendations.recommendations.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Recommendations
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Assessment 
                    color={getStrengthColor(results.recommendations.case_strength.overall)} 
                    sx={{ mr: 2 }} 
                  />
                  <Box>
                    <Typography variant="h6">
                      {results.recommendations.case_strength.overall}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Case Strength
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Case Summary */}
        <Card sx={{ mb: 3 }}>
          <CardHeader 
            title="Case Summary" 
            avatar={<Description color="primary" />}
          />
          <CardContent>
            <Typography variant="body1" paragraph>
              {results.case_summary}
            </Typography>
          </CardContent>
        </Card>

        {/* Document Summaries */}
        <Accordion sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">Document Summaries ({results.document_summaries.length})</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {results.document_summaries.map((doc, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {doc.document_type}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Case: {doc.case_number} | Court: {doc.court}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        Parties: {doc.parties}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {doc.summary}
                      </Typography>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Key Issues:
                        </Typography>
                        {doc.key_legal_issues.map((issue, i) => (
                          <Chip key={i} label={issue} size="small" sx={{ mr: 1, mt: 1 }} />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Timeline */}
        <Accordion sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">Event Timeline ({results.events.length})</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Event Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Parties Involved</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.events
                    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                    .map((event, index) => (
                    <TableRow key={index}>
                      <TableCell>{new Date(event.date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Chip label={event.event_type} size="small" />
                      </TableCell>
                      <TableCell>{event.description}</TableCell>
                      <TableCell>
                        {event.parties_involved.map((party, i) => (
                          <Chip key={i} label={party} size="small" variant="outlined" sx={{ mr: 1 }} />
                        ))}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>

        {/* Legal Analysis */}
        <Grid container spacing={3}>
          {/* Recommendations */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader 
                title="Legal Recommendations" 
                avatar={<Gavel color="primary" />}
              />
              <CardContent>
                <List>
                  {results.recommendations.recommendations.map((rec, index) => (
                    <ListItem key={index} divider>
                      <ListItemIcon>
                        <Chip 
                          label={rec.priority} 
                          color={getPriorityColor(rec.priority)}
                          size="small"
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={rec.action}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Category: {rec.category} | Timeline: {rec.timeline}
                            </Typography>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              {rec.rationale}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Case Strength */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader 
                title="Case Strength Analysis" 
                avatar={<Assessment color="primary" />}
              />
              <CardContent>
                <Box mb={2}>
                  <Typography variant="h6" gutterBottom>
                    Overall Strength: 
                    <Chip 
                      label={results.recommendations.case_strength.overall}
                      color={getStrengthColor(results.recommendations.case_strength.overall)}
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Score: {results.recommendations.case_strength.score}/100
                  </Typography>
                </Box>

                <Typography variant="h6" color="success.main" gutterBottom>
                  Strengths:
                </Typography>
                <List dense>
                  {results.recommendations.case_strength.strengths.map((strength, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={strength} />
                    </ListItem>
                  ))}
                </List>

                <Typography variant="h6" color="error.main" gutterBottom>
                  Weaknesses:
                </Typography>
                <List dense>
                  {results.recommendations.case_strength.weaknesses.map((weakness, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={weakness} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Action Buttons */}
        <Box display="flex" justifyContent="space-between" mt={4}>
          <Button
            variant="outlined"
            onClick={() => navigate('/')}
          >
            New Analysis
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => setExportDialog(true)}
          >
            Export Results
          </Button>
        </Box>

        {/* Export Dialog */}
        <Dialog open={exportDialog} onClose={() => setExportDialog(false)}>
          <DialogTitle>Export Results</DialogTitle>
          <DialogContent>
            <Typography gutterBottom>
              Choose export format for your analysis results:
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={4}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => handleExport('excel')}
                  disabled={exporting}
                >
                  Excel
                </Button>
              </Grid>
              <Grid item xs={4}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => handleExport('json')}
                  disabled={exporting}
                >
                  JSON
                </Button>
              </Grid>
              <Grid item xs={4}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => handleExport('pdf')}
                  disabled={exporting}
                >
                  PDF
                </Button>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setExportDialog(false)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default ResultsPage;
