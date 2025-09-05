# AI-Powered Legal Document Analysis System

A complete production-ready system for analyzing legal documents using AI agents, specifically designed for Indian Law. The system extracts key information, generates timelines, and provides actionable legal recommendations.

## 🏗️ Architecture

### Backend (FastAPI)
- **Document Processing**: PDF and image text extraction
- **AI Agent Pipeline**: Multi-agent analysis system
- **Export Services**: Excel, JSON, and PDF report generation
- **RESTful API**: Complete API for frontend integration

### Frontend Options
1. **Simple Frontend** (`frontend-simple/`): Vanilla JS, no dependencies
2. **React Frontend** (`frontend/`): Modern React with TypeScript (requires npm)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Modern web browser
- For React frontend: Node.js 16+ and npm

### 1. Backend Setup

```bash
# Navigate to project root
cd legal-analysis-app

# Configure Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup (Simple Version)

```bash
# In a new terminal, navigate to simple frontend
cd legal-analysis-app/frontend-simple

# Start HTTP server
python3 -m http.server 3000

# Open browser to http://localhost:3000
```

### 3. Frontend Setup (React Version - if npm works)

```bash
# Navigate to React frontend
cd legal-analysis-app/frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📁 Project Structure

```
legal-analysis-app/
├── backend/                     # FastAPI backend
│   ├── main.py                 # Main API application
│   ├── models.py               # Pydantic data models
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   └── services/               # Business logic
│       ├── document_processor.py
│       ├── ai_agents.py
│       └── export_service.py
├── frontend/                    # React frontend (TypeScript)
│   ├── package.json
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API integration
│   │   ├── types/              # TypeScript definitions
│   │   └── context/            # State management
│   └── public/
├── frontend-simple/             # Vanilla JS frontend
│   ├── index.html              # Main HTML page
│   ├── app.js                  # JavaScript logic
│   └── README.md               # Simple frontend docs
└── test_api.py                 # API testing script
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `POST /upload` - Upload documents for analysis
- `POST /analyze/{job_id}` - Start analysis process
- `GET /status/{job_id}` - Check analysis progress
- `GET /results/{job_id}` - Retrieve analysis results
- `GET /export/{job_id}?format={format}` - Export results
- `DELETE /jobs/{job_id}` - Cancel/delete analysis job

### Supported File Formats
- **Documents**: PDF
- **Images**: JPG, JPEG, PNG

### Export Formats
- **Excel**: Comprehensive report with multiple sheets
- **JSON**: Raw analysis data
- **PDF**: Formatted summary report

## 🤖 AI Agent Pipeline

The system uses a multi-agent approach for comprehensive analysis:

### 1. Document Summarizer Agent
- Extracts case metadata (title, number, court, parties)
- Generates case summary
- Identifies key legal concepts

### 2. Enhanced Date Extractor Agent
- Extracts chronological events
- Associates events with specific parties
- Maintains temporal relationships

### 3. Legal Recommendations Agent
- Provides actionable legal advice
- Categorizes recommendations by priority
- Offers strategic guidance

## 🧪 Testing

### API Testing
```bash
# Run comprehensive API tests
python test_api.py
```

### Manual Testing
1. Start both backend and frontend
2. Navigate to `http://localhost:3000`
3. Upload a legal document (PDF/image)
4. Monitor analysis progress
5. Review results and export reports

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# AI/LLM Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# File Upload Limits
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png

# Export Configuration
EXPORT_DIR=./exports
```

### Backend Configuration
Edit `backend/config.py` to customize:
- File upload limits
- AI model selection
- Export settings
- Logging configuration

## 🚀 Production Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment
```bash
# Simple frontend - serve static files
# React frontend - build and serve
npm run build
```

### Docker Support
```dockerfile
# Backend Dockerfile example
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🛠️ Development

### Adding New AI Agents
1. Create agent class in `services/ai_agents.py`
2. Implement required methods: `analyze()`, `parse_response()`
3. Add to orchestrator pipeline
4. Update models in `models.py`

### Frontend Customization
- **Simple**: Edit HTML/CSS/JS directly
- **React**: Standard React component development

### Database Integration
For production, replace in-memory job storage:
```python
# Replace jobs dict with database
from sqlalchemy import create_engine
# Implement job persistence
```

## 📊 Features

### Document Analysis
- ✅ PDF text extraction
- ✅ Image OCR processing
- ✅ Multi-page document support
- ✅ Legal document structure recognition

### AI Analysis
- ✅ Case summary generation
- ✅ Event timeline extraction
- ✅ Legal recommendation engine
- ✅ Party-specific analysis

### Export & Reporting
- ✅ Excel reports with multiple sheets
- ✅ JSON data export
- ✅ PDF summary reports
- ✅ Timeline visualization

### User Interface
- ✅ Drag & drop file upload
- ✅ Real-time progress tracking
- ✅ Responsive design
- ✅ Export management

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python environment
python --version
pip list

# Verify dependencies
pip install -r requirements.txt
```

#### Frontend Dependencies Failed
- Use the simple frontend (`frontend-simple/`) as an alternative
- Check npm registry configuration
- Try yarn instead of npm

#### Analysis Takes Too Long
- Check AI API quotas and limits
- Verify document size and complexity
- Monitor backend logs for errors

#### CORS Issues
- Ensure frontend URL is in CORS allowed origins
- Check browser developer console for errors

### Logging
Backend logs include:
- Document processing status
- AI agent execution details
- Error messages and stack traces

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check backend logs for errors
4. Test with provided sample files

## 🔄 Version History

- **v1.0.0**: Initial release with complete AI pipeline
  - Multi-agent document analysis
  - React and vanilla JS frontends
  - Export functionality
  - Production-ready backend
