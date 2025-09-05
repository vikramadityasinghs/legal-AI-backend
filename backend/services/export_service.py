import os
import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from config import settings

class ExportService:
    """
    Service for exporting analysis results in various formats
    """
    
    def __init__(self):
        self.export_dir = settings.EXPORT_DIR
    
    async def export_results(self, results: Dict[str, Any], format: str, job_id: str) -> str:
        """
        Export analysis results in specified format
        Returns path to exported file
        """
        if format == "excel":
            return await self._export_excel(results, job_id)
        elif format == "json":
            return await self._export_json(results, job_id)
        elif format == "pdf":
            return await self._export_pdf(results, job_id)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def _export_excel(self, results: Dict[str, Any], job_id: str) -> str:
       
        try:
            print(f"📊 Starting Excel export for job: {job_id}")
            print(f"📋 Results keys: {list(results.keys())}")
            
            import pandas as pd
            import os
            
            # Create export directory if it doesn't exist
            os.makedirs(self.export_dir, exist_ok=True)
            print(f"📁 Export directory: {self.export_dir}")
            
            # Generate Excel filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"legal_analysis_{job_id}_{timestamp}.xlsx"
            excel_path = os.path.join(self.export_dir, excel_filename)
            
            print(f"📄 Creating Excel file: {excel_path}")
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                
                # 1. Case Summary Sheet
                print("📝 Creating Case Summary sheet...")
                case_summary = results.get("case_summary", "No case summary available")
                summary_data = {
                    "Field": ["Job ID", "Status", "Cached", "Case Summary", "Total Documents", "Total Events", "Analysis Date"],
                    "Value": [
                        results.get("job_id", job_id),
                        results.get("status", "completed"),
                        results.get("cached", False),
                        case_summary,
                        len(results.get("document_summaries", [])),
                        len(results.get("events", [])),
                        results.get("completed_at", "")
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Case Summary', index=False)
                print(f"✅ Case Summary sheet created")
                
                # 2. Document Summaries Sheet
                print("📋 Creating Document Summaries sheet...")
                document_summaries = results.get("document_summaries", [])
                if document_summaries:
                    doc_data = []
                    for doc in document_summaries:
                        # Handle Pydantic DocumentSummary objects
                        if hasattr(doc, 'case_number'):
                            # Pydantic object - use direct attribute access
                            doc_data.append({
                                "Case Number": doc.case_number,
                                "Parties": doc.parties,
                                "Court": doc.court,
                                "Document Type": doc.document_type,
                                "Summary": doc.summary,
                                "Key Legal Issues": ", ".join(doc.key_legal_issues),
                                "Confidence": doc.confidence
                            })
                        else:
                            # Dictionary - use .get() method
                            doc_data.append({
                                "Case Number": doc.get("case_number", ""),
                                "Parties": doc.get("parties", ""),
                                "Court": doc.get("court", ""),
                                "Document Type": doc.get("document_type", ""),
                                "Summary": doc.get("summary", ""),
                                "Key Legal Issues": ", ".join(doc.get("key_legal_issues", [])),
                                "Confidence": doc.get("confidence", 0.0)
                            })
                    
                    doc_df = pd.DataFrame(doc_data)
                    doc_df.to_excel(writer, sheet_name='Document Summaries', index=False)
                    print(f"✅ Document Summaries sheet created with {len(doc_data)} documents")
                else:
                    # Create empty sheet with headers
                    empty_doc_df = pd.DataFrame(columns=["Case Number", "Parties", "Court", "Document Type", "Summary", "Key Legal Issues", "Confidence"])
                    empty_doc_df.to_excel(writer, sheet_name='Document Summaries', index=False)
                    print("⚠️ Document Summaries sheet created (empty)")
                
                # 3. Timeline Events Sheet
                print("📅 Creating Timeline Events sheet...")
                events = results.get("events", [])
                if events:
                    event_data = []
                    for event in events:
                        # Handle both Pydantic ExtractedEvent objects and dictionaries
                        if hasattr(event, 'date'):
                            # Pydantic object - use direct attribute access
                            event_data.append({
                                "Date": event.date,
                                "Event Type": event.event_type,
                                "Description": event.description,
                                "Parties Involved": ", ".join(event.parties_involved),
                                "Confidence": event.confidence,
                                "Document Source": event.document_source
                            })
                        else:
                            # Dictionary - use .get() method
                            event_data.append({
                                "Date": event.get("date", ""),
                                "Event Type": event.get("event_type", ""),
                                "Description": event.get("description", ""),
                                "Parties Involved": ", ".join(event.get("parties_involved", [])),
                                "Confidence": event.get("confidence", 0.0),
                                "Document Source": event.get("document_source", "")
                            })
                    
                    events_df = pd.DataFrame(event_data)
                    events_df.to_excel(writer, sheet_name='Timeline Events', index=False)
                    print(f"✅ Timeline Events sheet created with {len(event_data)} events")
                else:
                    # Create empty sheet with headers
                    empty_events_df = pd.DataFrame(columns=["Date", "Event Type", "Description", "Parties Involved", "Confidence", "Document Source"])
                    empty_events_df.to_excel(writer, sheet_name='Timeline Events', index=False)
                    print("⚠️ Timeline Events sheet created (empty)")
                
                # 4. Legal Recommendations Sheet
                print("⚖️ Creating Legal Recommendations sheet...")
                recommendations_data = results.get("recommendations", {})
                
                # Handle LegalAnalysis Pydantic object properly
                if recommendations_data:
                    if hasattr(recommendations_data, 'recommendations'):
                        # Pydantic LegalAnalysis object - use direct attribute access
                        recommendations = recommendations_data.recommendations
                        case_strength = recommendations_data.case_strength
                        legal_analysis = recommendations_data.legal_analysis
                        next_steps = recommendations_data.next_steps
                    else:
                        # Dictionary - use .get() method
                        recommendations = recommendations_data.get("recommendations", [])
                        case_strength = recommendations_data.get("case_strength", {})
                        legal_analysis = recommendations_data.get("legal_analysis", "")
                        next_steps = recommendations_data.get("next_steps", [])
                else:
                    recommendations = []
                    case_strength = None
                    legal_analysis = ""
                    next_steps = []
                
                if recommendations:
                    rec_data = []
                    for rec in recommendations:
                        # Handle both Pydantic LegalRecommendation objects and dictionaries
                        if hasattr(rec, 'category'):
                            # Pydantic object - use direct attribute access
                            rec_data.append({
                                "Category": rec.category,
                                "Priority": rec.priority,
                                "Action": rec.action,
                                "Legal Basis": rec.legal_basis,
                                "Timeline": rec.timeline,
                                "Rationale": rec.rationale
                            })
                        else:
                            # Dictionary - use .get() method
                            rec_data.append({
                                "Category": rec.get("category", ""),
                                "Priority": rec.get("priority", ""),
                                "Action": rec.get("action", ""),
                                "Legal Basis": rec.get("legal_basis", ""),
                                "Timeline": rec.get("timeline", ""),
                                "Rationale": rec.get("rationale", "")
                            })
                    
                    rec_df = pd.DataFrame(rec_data)
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
                    print(f"✅ Recommendations sheet created with {len(rec_data)} recommendations")
                else:
                    # Create empty sheet with headers
                    empty_rec_df = pd.DataFrame(columns=["Category", "Priority", "Action", "Legal Basis", "Timeline", "Rationale"])
                    empty_rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
                    print("⚠️ Recommendations sheet created (empty)")
                
                # 5. Case Strength Analysis Sheet
                print("💪 Creating Case Strength sheet...")
                if case_strength:
                    # Handle both Pydantic CaseStrength objects and dictionaries
                    if hasattr(case_strength, 'overall'):
                        # Pydantic CaseStrength object
                        strength_data = {
                            "Metric": ["Overall Assessment", "Score", "Legal Analysis", "Strengths", "Weaknesses", "Next Steps"],
                            "Value": [
                                case_strength.overall,
                                case_strength.score,
                                legal_analysis,
                                "; ".join(case_strength.strengths),
                                "; ".join(case_strength.weaknesses),
                                "; ".join(next_steps) if isinstance(next_steps, list) else next_steps
                            ]
                        }
                    else:
                        # Dictionary
                        strength_data = {
                            "Metric": ["Overall Assessment", "Score", "Legal Analysis", "Strengths", "Weaknesses", "Next Steps"],
                            "Value": [
                                case_strength.get("overall", ""),
                                case_strength.get("score", 0.0),
                                legal_analysis,
                                "; ".join(case_strength.get("strengths", [])),
                                "; ".join(case_strength.get("weaknesses", [])),
                                "; ".join(next_steps) if isinstance(next_steps, list) else next_steps
                            ]
                        }
                    
                    strength_df = pd.DataFrame(strength_data)
                    strength_df.to_excel(writer, sheet_name='Case Strength', index=False)
                    print(f"✅ Case Strength sheet created")
                else:
                    # Create empty sheet
                    empty_strength_df = pd.DataFrame(columns=["Metric", "Value"])
                    empty_strength_df.to_excel(writer, sheet_name='Case Strength', index=False)
                    print("⚠️ Case Strength sheet created (empty)")
                
                # 6. Extraction Stats Sheet
                print("📊 Creating Extraction Stats sheet...")
                extraction_stats = results.get("extraction_stats", {})
                if extraction_stats:
                    stats_data = {
                        "Statistic": ["Total Files", "Success Count", "Error Count"],
                        "Value": [
                            extraction_stats.get("total_files", 0),
                            extraction_stats.get("success_count", 0),
                            extraction_stats.get("error_count", 0)
                        ]
                    }
                    
                    # Add file processing details
                    files_processed = extraction_stats.get("files_processed", [])
                    if files_processed:
                        for i, file_info in enumerate(files_processed):
                            stats_data["Statistic"].append(f"File {i+1} Name")
                            stats_data["Value"].append(file_info.get("filename", ""))
                            stats_data["Statistic"].append(f"File {i+1} Status")
                            stats_data["Value"].append(file_info.get("status", ""))
                            stats_data["Statistic"].append(f"File {i+1} Text Length")
                            stats_data["Value"].append(file_info.get("text_length", 0))
                    
                    stats_df = pd.DataFrame(stats_data)
                    stats_df.to_excel(writer, sheet_name='Extraction Stats', index=False)
                    print(f"✅ Extraction Stats sheet created")
                else:
                    # Create empty sheet
                    empty_stats_df = pd.DataFrame(columns=["Statistic", "Value"])
                    empty_stats_df.to_excel(writer, sheet_name='Extraction Stats', index=False)
                    print("⚠️ Extraction Stats sheet created (empty)")
            
            print(f"✅ Excel file created successfully: {excel_path}")
            return excel_path
            
        except Exception as e:
            print(f"❌ Excel export error: {e}")
            print(f"🔍 Error type: {type(e)}")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            raise Exception(f"Excel export failed: {str(e)}")
    async def _export_json(self, results: Dict[str, Any], job_id: str) -> str:
        """Export complete results to JSON"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"legal_analysis_{job_id}_{timestamp}.json"
            file_path = os.path.join(self.export_dir, filename)
            
            # Prepare export data
            export_data = {
                "export_info": {
                    "job_id": job_id,
                    "export_date": datetime.now().isoformat(),
                    "format": "json",
                    "version": "1.0"
                },
                "analysis_results": results
            }
            
            # Save to JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"JSON export failed: {str(e)}")
    
    async def _export_pdf(self, results: Dict[str, Any], job_id: str) -> str:
        """Export results to PDF report"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"legal_report_{job_id}_{timestamp}.pdf"
            file_path = os.path.join(self.export_dir, filename)
            
            # For now, create a text-based PDF using simple text formatting
            # In production, you would use reportlab or similar for better formatting
            
            report_content = self._generate_text_report(results, job_id)
            
            # Save as text file with PDF extension (placeholder)
            # In production, implement proper PDF generation
            with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Return text file path for now
            return file_path.replace('.pdf', '.txt')
            
        except Exception as e:
            raise Exception(f"PDF export failed: {str(e)}")
    
    def _generate_text_report(self, results: Dict[str, Any], job_id: str) -> str:
        """Generate text-based report"""
        report_lines = [
            "="*60,
            "AI-POWERED LEGAL DOCUMENT ANALYSIS REPORT",
            "="*60,
            f"Job ID: {job_id}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "CASE SUMMARY:",
            "-"*20,
            results.get("case_summary", "No summary available"),
            "",
            "DOCUMENT ANALYSIS:",
            "-"*20
        ]
        
        # Add document summaries
        summaries = results.get("document_summaries", [])
        for i, summary in enumerate(summaries, 1):
            report_lines.extend([
                f"Document {i}:",
                f"  Case Number: {summary.get('case_number', 'Unknown')}",
                f"  Parties: {summary.get('parties', 'Unknown')}",
                f"  Court: {summary.get('court', 'Unknown')}",
                f"  Type: {summary.get('document_type', 'Unknown')}",
                f"  Summary: {summary.get('summary', 'No summary')[:200]}...",
                ""
            ])
        
        # Add timeline events
        report_lines.extend([
            "TIMELINE OF EVENTS:",
            "-"*20
        ])
        
        events = results.get("events", [])
        for i, event in enumerate(events[:20], 1):  # Top 20 events
            report_lines.extend([
                f"{i}. {event.get('date', 'Unknown')} - {event.get('event_type', 'Unknown')}",
                f"   {event.get('description', 'No description')}",
                ""
            ])
        
        # Add recommendations
        recommendations = results.get("recommendations", {})
        if recommendations:
            report_lines.extend([
                "LEGAL RECOMMENDATIONS:",
                "-"*25
            ])
            
            for i, rec in enumerate(recommendations.get("recommendations", []), 1):
                report_lines.extend([
                    f"{i}. [{rec.get('priority', 'Medium')}] {rec.get('category', 'General')}",
                    f"   Action: {rec.get('action', 'No action specified')}",
                    f"   Legal Basis: {rec.get('legal_basis', 'Not specified')}",
                    f"   Timeline: {rec.get('timeline', 'Not specified')}",
                    ""
                ])
            
            # Case strength
            case_strength = recommendations.get("case_strength", {})
            if case_strength:
                report_lines.extend([
                    "CASE STRENGTH ASSESSMENT:",
                    "-"*30,
                    f"Overall: {case_strength.get('overall', 'Moderate')}",
                    f"Score: {case_strength.get('score', 0.5):.2f}",
                    "",
                    "Strengths:",
                ])
                
                for strength in case_strength.get("strengths", []):
                    report_lines.append(f"  + {strength}")
                
                report_lines.append("")
                report_lines.append("Weaknesses:")
                
                for weakness in case_strength.get("weaknesses", []):
                    report_lines.append(f"  - {weakness}")
        
        # Add footer
        report_lines.extend([
            "",
            "="*60,
            "Report generated by AI Legal Analysis System",
            "For Indian Law | Multi-Agent AI Analysis",
            "="*60
        ])
        
        return "\\n".join(report_lines)
