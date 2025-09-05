# AI-Powered Legal Document Analysis - Backend API

## FastAPI Backend for Legal Document Analysis

This backend provides REST API endpoints for the legal document analysis system, extracting the core functionality from the Jupyter notebook into a production-ready service.

### Features
- Document upload and text extraction
- Multi-agent AI analysis (Summarizer, Date Extractor, Legal Recommendations)
- RESTful API endpoints
- File processing with OCR and PDF parsing
- Export capabilities

### API Endpoints
- `POST /api/upload` - Upload legal documents
- `POST /api/analyze` - Run complete analysis pipeline
- `GET /api/results/{job_id}` - Get analysis results
- `GET /api/export/{job_id}/{format}` - Export results

### Tech Stack
- FastAPI for REST API
- Pydantic for data validation
- LangChain for AI agents
- Azure OpenAI for LLM
- PyMuPDF for PDF processing
- Pytesseract for OCR
