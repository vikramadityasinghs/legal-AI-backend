from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
import uvicorn
import os
import uuid
import json
from datetime import datetime
import aiofiles
import tempfile
import shutil

from models import (
    AnalysisRequest,
    AnalysisResponse,
    JobStatus,
    DocumentSummary,
    ExtractedEvent,
    LegalRecommendation
)
from services.document_processor import DocumentProcessor
from services.ai_agents import AIAgentOrchestrator
from services.export_service import ExportService
from services.cache_service import CaseCacheService
from services.summary_service import SummaryService
from config import settings
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="AI Legal Document Analysis API",
    description="Complete legal document analysis for Indian Law",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Global services
document_processor = DocumentProcessor()
ai_orchestrator = AIAgentOrchestrator()
export_service = ExportService()
cache_service = CaseCacheService()
summary_service = SummaryService("../summaries")

# In-memory job storage (use Redis in production)
jobs = {}


@app.get("/swagger", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="ENI Claims APIs")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Legal Document Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/upload", response_model=dict)
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload legal documents for analysis
    Supports PDF, JPG, PNG formats
    Checks cache for existing analysis
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job directory
        job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Save uploaded files and collect file info
        uploaded_files = []
        file_names = []
        temp_files = []
        
        for file in files:
            if not file.filename:
                continue
                
            # Validate file type
            if not any(file.filename.lower().endswith(ext) 
                      for ext in ['.pdf', '.jpg', '.jpeg', '.png']):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file.filename}"
                )
            
            # Read file content for cache checking
            content = await file.read()
            
            # Save file
            file_path = os.path.join(job_dir, file.filename)
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "type": file.content_type
            })
            
            file_names.append(file.filename)
            temp_files.append(content)  # For cache checking
        
        # Check cache by file hash first
        cached_result = cache_service.check_cache_by_files(temp_files)
        
        # If not found by hash, check by content (file names, case indicators)
        if not cached_result:
            cached_result = cache_service.check_cache_by_content(file_names)
        
        # Initialize job status
        job_data = {
            "status": "uploaded",
            "created_at": datetime.now().isoformat(),
            "files": uploaded_files,
            "progress": 0,
            "current_step": "Files uploaded successfully",
            "cached_result": cached_result is not None,
            "file_names": file_names,
            "cache_hit": False,
            "completed_steps": []
        }
        
        # If we found a cached result, mark job as completed and prepare downloads
        if cached_result:
            # Generate Excel file for cached result
            excel_file_path = None
            try:
                excel_file_path = await export_service.export_results(
                    cached_result, 
                    "excel", 
                    job_id
                )
            except Exception as e:
                print(f"Failed to generate Excel file for cached result: {e}")
            
            job_data.update({
                "status": "completed",
                "progress": 100,
                "current_step": "Analysis completed (from cache)",
                "result": cached_result,
                "completed_at": datetime.now().isoformat(),
                "completed_steps": ["document_processing", "text_extraction", "ai_analysis", "generating_report"],
                "cache_hit": True,
                "downloads": {
                    "excel_available": excel_file_path is not None,
                    "excel_url": f"/download/excel/{job_id}" if excel_file_path else None,
                    "json_url": f"/download/json/{job_id}",
                    "summary_text": cached_result.get("case_summary", "")
                }
            })
        
        jobs[job_id] = job_data
        
        response = {
            "job_id": job_id,
            "files_uploaded": len(uploaded_files),
            "status": "success",
            "cached": cached_result is not None,
            "instant_results": cached_result is not None
        }
        
        if cached_result:
            response["message"] = "Files uploaded and analysis found in cache! Results available immediately."
            response["result_available"] = True
        else:
            response["message"] = "Files uploaded successfully. Use /analyze to start processing."
            response["result_available"] = False
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/{job_id}", response_model=dict)
async def analyze_documents(
    job_id: str,
    background_tasks: BackgroundTasks
):
    """
    Start analysis of uploaded documents
    Runs the complete AI pipeline in background
    Returns immediately if cached result is available
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # If already cached/completed, return immediately
    if job.get("cached_result") or job["status"] == "completed":
        return {
            "job_id": job_id,
            "status": "completed",
            "message": "Analysis completed (from cache)" if job.get("cache_hit") else "Analysis already completed",
            "cached": job.get("cache_hit", False)
        }
    
    if job["status"] != "uploaded":
        raise HTTPException(status_code=400, detail="Job already processed or in progress")
    
    # Update job status
    jobs[job_id]["status"] = "processing"
    jobs[job_id]["progress"] = 10
    jobs[job_id]["current_step"] = "Starting analysis..."
    
    # Start background processing
    background_tasks.add_task(process_documents, job_id)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Analysis started. Check status with /status/{job_id}"
    }

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get current status of analysis job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        created_at=job["created_at"],
        cache_hit=job.get("cache_hit", False),
        completed_steps=job.get("completed_steps", [])
    )

@app.get("/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Get complete analysis results with summary and download links"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    # Get result from either cached result or fresh analysis
    result_data = job.get("result") or job.get("results")
    if not result_data:
        raise HTTPException(status_code=500, detail="Analysis results not found")
    
    # Generate Excel file if not already exists
    excel_file_path = None
    try:
        excel_file_path = await export_service.export_results(
            result_data, 
            "excel", 
            job_id
        )
    except Exception as e:
        print(f"Failed to generate Excel file: {e}")
    
    response = {
        "job_id": job_id,
        "status": "completed",
        "cached": job.get("cache_hit", False),
        "case_summary": result_data.get("case_summary", ""),
        "document_summaries": result_data.get("document_summaries", []),
        "events": result_data.get("events", []),
        "recommendations": result_data.get("recommendations", {}),
        "extraction_stats": result_data.get("extraction_stats", {}),
        "completed_at": result_data.get("completed_at", ""),
        "downloads": {
            "excel_available": excel_file_path is not None,
            "excel_url": f"/download/excel/{job_id}" if excel_file_path else None,
            "json_url": f"/download/json/{job_id}",
            "summary_text": result_data.get("case_summary", "")
        }
    }
    
    return response

@app.get("/download/excel/{job_id}")
async def download_excel(job_id: str):
    """Download Excel file for analysis results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    try:
        result_data = job.get("result") or job.get("results")
        if not result_data:
            raise HTTPException(status_code=500, detail="Analysis results not found")
        
        file_path = await export_service.export_results(
            result_data, 
            "excel", 
            job_id
        )
        
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"legal_analysis_{job_id}.xlsx",
            headers={"Content-Disposition": f"attachment; filename=legal_analysis_{job_id}.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel download failed: {str(e)}")

@app.get("/download/json/{job_id}")
async def download_json(job_id: str):
    """Download JSON file for analysis results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    try:
        result_data = job.get("result") or job.get("results")
        if not result_data:
            raise HTTPException(status_code=500, detail="Analysis results not found")
        
        file_path = await export_service.export_results(
            result_data, 
            "json", 
            job_id
        )
        
        return FileResponse(
            file_path,
            media_type="application/json",
            filename=f"legal_analysis_{job_id}.json",
            headers={"Content-Disposition": f"attachment; filename=legal_analysis_{job_id}.json"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON download failed: {str(e)}")

@app.get("/export/{job_id}")
async def export_results(job_id: str, format: str = "excel"):
    """
    Export analysis results in various formats
    Supported formats: excel, json, pdf
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    try:
        file_path = await export_service.export_results(
            job["results"], 
            format, 
            job_id
        )
        
        # Determine media type based on format
        media_types = {
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json",
            "pdf": "application/pdf"
        }
        
        return FileResponse(
            file_path,
            media_type=media_types.get(format, "application/octet-stream"),
            filename=f"legal_analysis_{job_id}.{format}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job and associated files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up files
    job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
    if os.path.exists(job_dir):
        shutil.rmtree(job_dir)
    
    # Remove from jobs
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}

# Cache Management Endpoints

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics and information"""
    try:
        stats = cache_service.get_cache_stats()
        return {
            "status": "success",
            "cache_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@app.get("/cache/search")
async def search_cached_cases(query: str = ""):
    """Search cached cases by query"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        results = cache_service.search_cached_cases(query)
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.delete("/cache/clear")
async def clear_old_cache(days: int = 30):
    """Clear cache entries older than specified days"""
    try:
        removed_count = cache_service.clear_old_cache(days)
        return {
            "status": "success",
            "message": f"Removed {removed_count} old cache entries",
            "removed_count": removed_count,
            "cutoff_days": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@app.get("/cache/list")
async def list_cached_cases():
    """List all cached cases with basic information"""
    try:
        stats = cache_service.get_cache_stats()
        return {
            "status": "success",
            "total_cases": stats["total_cached_cases"],
            "recent_cases": stats["recent_cases"],
            "most_accessed": stats["most_accessed_cases"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cached cases: {str(e)}")

@app.get("/cache/case/{case_id}")
async def get_cached_case_result(case_id: str):
    """
    Get the full cached analysis result for a specific case ID with downloads
    """
    try:
        # Get the cached case result
        cached_result = cache_service.get_cached_case_by_id(case_id)
        
        if not cached_result:
            raise HTTPException(status_code=404, detail="Cached case not found")
        
        # Create a temporary job for this cached result to enable downloads
        temp_job_id = f"cache_{case_id}"
        
        # Extract case summary - try summary service first, then cached data
        case_summary = summary_service.get_summary(case_id)
        
        if not case_summary:
            # Fallback to extracting from cached data structure
            if "agent_outputs" in cached_result and "agent1_summary" in cached_result["agent_outputs"]:
                case_summary = cached_result["agent_outputs"]["agent1_summary"].get("content", "")
            elif "case_summary" in cached_result:
                case_summary = cached_result["case_summary"]
            else:
                case_summary = ""
        
        # Extract events from the cached data structure (simplified)
        events = []
        if "agent_outputs" in cached_result and "agent2_dates" in cached_result["agent_outputs"]:
            agent2_data = cached_result["agent_outputs"]["agent2_dates"]
            if "metadata" in agent2_data and "events" in agent2_data["metadata"]:
                events = agent2_data["metadata"]["events"]
                print(f"Successfully extracted {len(events)} events from agent2_dates")
        elif "events" in cached_result:
            events = cached_result["events"]
            print(f"Found {len(events)} events in direct events array")
        
        # Extract document summaries
        document_summaries = []
        if "agent_outputs" in cached_result and "agent1_summary" in cached_result["agent_outputs"]:
            agent1_data = cached_result["agent_outputs"]["agent1_summary"]
            if "metadata" in agent1_data and "document_summaries" in agent1_data["metadata"]:
                document_summaries = agent1_data["metadata"]["document_summaries"]
        elif "document_summaries" in cached_result:
            document_summaries = cached_result["document_summaries"]
        
        # Extract recommendations
        recommendations = {}
        if "agent_outputs" in cached_result:
            # Look for recommendations in any agent output
            for agent_key, agent_data in cached_result["agent_outputs"].items():
                if isinstance(agent_data, dict) and "recommendations" in agent_data:
                    recommendations = agent_data["recommendations"]
                    break
        elif "recommendations" in cached_result:
            recommendations = cached_result["recommendations"]
        
        # Generate Excel file for cached result
        excel_file_path = None
        try:
            excel_file_path = await export_service.export_results(
                cached_result, 
                "excel", 
                temp_job_id
            )
        except Exception as e:
            print(f"Failed to generate Excel file for cached result: {e}")
        
        response = {
            "job_id": temp_job_id,
            "status": "completed",
            "cached": True,
            "case_summary": case_summary,
            "document_summaries": document_summaries,
            "events": events,
            "recommendations": recommendations,
            "extraction_stats": cached_result.get("metadata", {}),
            "completed_at": cached_result.get("metadata", {}).get("generated_at", ""),
            "downloads": {
                "excel_available": excel_file_path is not None,
                "excel_url": f"/download/excel/cache_{case_id}" if excel_file_path else None,
                "json_url": f"/download/json/cache_{case_id}",
                "summary_text": case_summary
            }
        }
        
        # Store this temporarily to enable downloads
        jobs[temp_job_id] = {
            "status": "completed",
            "result": cached_result,
            "cache_hit": True
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Summary Management Endpoints

@app.get("/summaries/list")
async def list_summaries():
    """List all available case summaries"""
    try:
        summaries = summary_service.list_summaries()
        stats = summary_service.get_summary_stats()
        
        return {
            "status": "success",
            "summaries": summaries,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list summaries: {str(e)}")

@app.get("/summaries/{case_id}")
async def get_summary(case_id: str):
    """Get a specific case summary"""
    try:
        summary = summary_service.get_summary(case_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return {
            "status": "success",
            "case_id": case_id,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@app.post("/summaries/{case_id}")
async def save_summary(case_id: str, summary: dict):
    """Save or update a case summary"""
    try:
        summary_content = summary.get("content", "")
        if not summary_content:
            raise HTTPException(status_code=400, detail="Summary content is required")
        
        file_path = summary_service.save_summary(case_id, summary_content)
        
        return {
            "status": "success",
            "case_id": case_id,
            "file_path": file_path,
            "message": "Summary saved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save summary: {str(e)}")

@app.delete("/summaries/{case_id}")
async def delete_summary(case_id: str):
    """Delete a case summary"""
    try:
        success = summary_service.delete_summary(case_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return {
            "status": "success",
            "case_id": case_id,
            "message": "Summary deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete summary: {str(e)}")

async def process_documents(job_id: str):
    """
    Background task to process documents through AI pipeline
    """
    try:
        job = jobs[job_id]
        job_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        
        # Step 1: Extract text from documents
        jobs[job_id]["progress"] = 20
        jobs[job_id]["current_step"] = "Extracting text from documents..."
        jobs[job_id]["completed_steps"] = ["document_processing"]
        
        extraction_results = await document_processor.process_directory(job_dir)
        
        # Step 2: Run Agent 1 (Document Summarizer)
        jobs[job_id]["progress"] = 40
        jobs[job_id]["current_step"] = "Generating document summaries..."
        jobs[job_id]["completed_steps"] = ["document_processing", "text_extraction"]
        
        summaries = await ai_orchestrator.run_document_summarizer(
            extraction_results["extracted_texts"]
        )
        
        # Step 3: Run Agent 2 (Enhanced Date Extractor)
        jobs[job_id]["progress"] = 60
        jobs[job_id]["current_step"] = "Extracting events and timeline..."
        jobs[job_id]["completed_steps"] = ["document_processing", "text_extraction", "ai_analysis"]
        
        events = await ai_orchestrator.run_date_extractor(
            extraction_results["extracted_texts"]
        )
        
        # Step 4: Generate case summary
        jobs[job_id]["progress"] = 80
        jobs[job_id]["current_step"] = "Generating case summary..."
        
        case_summary = await ai_orchestrator.generate_case_summary(summaries, events)
        
        # Step 5: Run Agent 5 (Legal Recommendations)
        jobs[job_id]["progress"] = 90
        jobs[job_id]["current_step"] = "Generating legal recommendations..."
        
        recommendations = await ai_orchestrator.run_legal_recommendations(
            summaries, events
        )
        
        # Finalize results
        jobs[job_id]["progress"] = 100
        jobs[job_id]["current_step"] = "Analysis completed"
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_steps"] = ["document_processing", "text_extraction", "ai_analysis", "generating_report"]
        
        analysis_result = {
            "job_id": job_id,
            "case_summary": case_summary,  # Changed from document_summary
            "document_summaries": summaries,  # Added this field
            "events": events,
            "recommendations": recommendations,
            "extraction_stats": extraction_results["stats"],
            "completed_at": datetime.now().isoformat()
        }
        
        jobs[job_id]["result"] = analysis_result
        
        # Generate Excel file for the completed analysis
        excel_file_path = None
        try:
            excel_file_path = await export_service.export_results(
                analysis_result, 
                "excel", 
                job_id
            )
        except Exception as e:
            print(f"Failed to generate Excel file: {e}")
        
        # Add download information to job
        jobs[job_id]["downloads"] = {
            "excel_available": excel_file_path is not None,
            "excel_url": f"/download/excel/{job_id}" if excel_file_path else None,
            "json_url": f"/download/json/{job_id}",
            "summary_text": analysis_result.get("case_summary", "")
        }
        
        # Cache the analysis result for future use
        try:
            # Get file paths for caching
            file_paths = []
            file_names = job.get("file_names", [])
            
            for filename in file_names:
                file_path = os.path.join(job_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        file_paths.append(f.read())
            
            if file_paths:
                cache_id = cache_service.cache_analysis(
                    files=file_paths,
                    file_names=file_names,
                    analysis_result=analysis_result
                )
                jobs[job_id]["cache_id"] = cache_id
                print(f"Analysis cached with ID: {cache_id}")
        
        except Exception as cache_error:
            print(f"Failed to cache analysis: {cache_error}")
            # Don't fail the entire analysis if caching fails
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["current_step"] = f"Analysis failed: {str(e)}"

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
