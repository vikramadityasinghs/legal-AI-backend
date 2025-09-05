// TypeScript type definitions for the legal analysis application

export interface DocumentSummary {
  case_number: string;
  parties: string;
  court: string;
  document_type: string;
  summary: string;
  key_legal_issues: string[];
  confidence: number;
}

export interface ExtractedEvent {
  date: string;
  event_type: string;
  description: string;
  parties_involved: string[];
  confidence: number;
  document_source?: string;
}

export interface LegalRecommendation {
  category: string;
  priority: 'High' | 'Medium' | 'Low';
  action: string;
  legal_basis: string;
  timeline: string;
  rationale: string;
}

export interface CaseStrength {
  overall: 'Strong' | 'Moderate' | 'Weak';
  strengths: string[];
  weaknesses: string[];
  score: number;
}

export interface LegalAnalysis {
  recommendations: LegalRecommendation[];
  case_strength: CaseStrength;
  legal_analysis: string;
  next_steps: string[];
}

export interface AnalysisResults {
  job_id: string;
  case_summary: string;
  document_summaries: DocumentSummary[];
  events: ExtractedEvent[];
  recommendations: LegalAnalysis;
  extraction_stats: {
    total_files: number;
    success_count: number;
    error_count: number;
    files_processed: Array<{
      filename: string;
      status: string;
      text_length: number;
      error?: string;
    }>;
  };
  completed_at: string;
}

export interface JobStatus {
  job_id: string;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  created_at: string;
  error?: string;
}

export interface UploadResponse {
  job_id: string;
  files_uploaded: number;
  status: string;
  message: string;
}

export interface UploadedFile {
  filename: string;
  size: number;
  type: string;
}

export interface AnalysisJob {
  job_id: string;
  files: UploadedFile[];
  status: JobStatus['status'];
  created_at: string;
}
