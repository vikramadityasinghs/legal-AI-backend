import os
import asyncio
from typing import List, Dict, Any
import aiofiles
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from config import settings

class DocumentProcessor:
    """
    Document processing service for text extraction from PDFs and images
    Extracted from the LSD tool functionality in the notebook
    """
    
    def __init__(self):
        self.supported_types = settings.SUPPORTED_FILE_TYPES
    
    async def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Process all documents in a directory
        Returns extraction results and statistics
        """
        results = {
            "extracted_texts": [],
            "stats": {
                "total_files": 0,
                "success_count": 0,
                "error_count": 0,
                "files_processed": []
            }
        }
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        files = [f for f in os.listdir(directory_path) 
                if any(f.lower().endswith(ext) for ext in self.supported_types)]
        
        results["stats"]["total_files"] = len(files)
        
        for filename in files:
            file_path = os.path.join(directory_path, filename)
            
            try:
                extracted_text = await self.extract_text_from_file(file_path)
                
                if extracted_text.strip():
                    results["extracted_texts"].append({
                        "filename": filename,
                        "content": extracted_text,
                        "file_path": file_path,
                        "text_length": len(extracted_text)
                    })
                    results["stats"]["success_count"] += 1
                    results["stats"]["files_processed"].append({
                        "filename": filename,
                        "status": "success",
                        "text_length": len(extracted_text)
                    })
                else:
                    results["stats"]["error_count"] += 1
                    results["stats"]["files_processed"].append({
                        "filename": filename,
                        "status": "no_text_found",
                        "text_length": 0
                    })
                    
            except Exception as e:
                results["stats"]["error_count"] += 1
                results["stats"]["files_processed"].append({
                    "filename": filename,
                    "status": "error",
                    "error": str(e),
                    "text_length": 0
                })
        
        return results
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from a single file based on its type"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return await self.extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return await self.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        def _extract():
            try:
                doc = fitz.open(pdf_path)
                text = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    text += page_text + "\\n"
                
                doc.close()
                return text.strip()
                
            except Exception as e:
                raise Exception(f"PDF extraction failed: {str(e)}")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract)
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR (Tesseract)"""
        def _extract():
            try:
                # Open and process image
                image = Image.open(image_path)
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Perform OCR
                text = pytesseract.image_to_string(
                    image, 
                    config=settings.TESSERACT_CONFIG
                )
                
                return text.strip()
                
            except Exception as e:
                raise Exception(f"OCR extraction failed: {str(e)}")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract)
    
    async def save_extracted_text(self, text: str, output_path: str) -> None:
        """Save extracted text to file"""
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(text)
