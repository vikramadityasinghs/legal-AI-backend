import axios from 'axios';
import { AnalysisResults, JobStatus, UploadResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export class LegalAnalysisAPI {
  /**
   * Upload legal documents for analysis
   */
  static async uploadDocuments(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Start analysis of uploaded documents
   */
  static async startAnalysis(jobId: string): Promise<{ job_id: string; status: string; message: string }> {
    const response = await api.post(`/api/analyze/${jobId}`);
    return response.data;
  }

  /**
   * Get job status and progress
   */
  static async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await api.get(`/api/status/${jobId}`);
    return response.data;
  }

  /**
   * Get analysis results
   */
  static async getAnalysisResults(jobId: string): Promise<AnalysisResults> {
    const response = await api.get(`/api/results/${jobId}`);
    return response.data;
  }

  /**
   * Export results in specified format
   */
  static async exportResults(jobId: string, format: 'excel' | 'json' | 'pdf'): Promise<Blob> {
    const response = await api.get(`/api/export/${jobId}/${format}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Delete job and associated files
   */
  static async deleteJob(jobId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/jobs/${jobId}`);
    return response.data;
  }

  /**
   * Health check
   */
  static async healthCheck(): Promise<{ message: string; version: string; status: string }> {
    const response = await api.get('/');
    return response.data;
  }
}

// Export axios instance for direct use if needed
export { api };

// Error handling utility
export const handleAPIError = (error: any): string => {
  if (error.response) {
    // Server responded with error status
    return error.response.data?.detail || error.response.data?.message || 'Server error occurred';
  } else if (error.request) {
    // Request was made but no response received
    return 'Network error - unable to connect to server';
  } else {
    // Something else happened
    return error.message || 'An unexpected error occurred';
  }
};

// Export a singleton instance for easy usage
export const apiService = LegalAnalysisAPI;
