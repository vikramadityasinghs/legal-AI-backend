# Simple Frontend for Legal Document Analysis System

This is a lightweight frontend implementation that works without Node.js dependencies. It uses vanilla JavaScript with modern ES6+ features and communicates directly with the FastAPI backend.

## Features

- **File Upload**: Drag & drop or click to upload PDF and image files
- **Real-time Progress**: Live updates during document analysis
- **Results Dashboard**: Comprehensive display of analysis results
- **Export Options**: Download results in Excel, PDF, or JSON format
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **HTML5**: Semantic markup with modern features
- **CSS3**: Responsive design with Tailwind CSS (via CDN)
- **JavaScript ES6+**: Vanilla JS with async/await, fetch API
- **Font Awesome**: Icons via CDN

## Getting Started

### Prerequisites

- Modern web browser with JavaScript enabled
- FastAPI backend running on `http://localhost:8000`

### Running the Frontend

1. Start the FastAPI backend:
   ```bash
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. Serve the frontend:
   ```bash
   # Option 1: Simple HTTP server with Python
   python -m http.server 3000
   
   # Option 2: Using any other web server
   # Just serve the files from this directory
   ```

3. Open your browser and navigate to `http://localhost:3000`

## File Structure

```
frontend-simple/
├── index.html          # Main HTML page with all UI components
├── app.js              # JavaScript application logic
└── README.md           # This file
```

## API Integration

The frontend communicates with the FastAPI backend through these endpoints:

- `POST /upload` - Upload documents for analysis
- `POST /analyze/{job_id}` - Start analysis process
- `GET /status/{job_id}` - Check analysis progress
- `GET /results/{job_id}` - Retrieve analysis results
- `GET /export/{job_id}` - Export results in various formats
- `DELETE /jobs/{job_id}` - Cancel/delete analysis job

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## Development Notes

This simple frontend is designed to work without build tools or package managers. It's perfect for:

- Quick prototyping
- Environments with restricted npm/yarn access
- Simple deployment scenarios
- Development testing

For production use with more advanced features, consider using the React frontend in the `frontend/` directory once npm issues are resolved.

## Customization

You can easily customize the interface by:

1. **Colors**: Modify the CSS custom properties and Tailwind classes
2. **Layout**: Adjust the HTML structure and CSS grid/flexbox layouts
3. **Features**: Add new JavaScript functions for additional functionality
4. **Styling**: Replace Tailwind with custom CSS or other frameworks

## Security Considerations

- The frontend assumes the backend is running on localhost
- For production deployment, update the `API_BASE_URL` in `app.js`
- Implement proper CORS configuration in the FastAPI backend
- Consider adding authentication if required
