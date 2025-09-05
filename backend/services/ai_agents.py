import asyncio
import json
import re
from typing import List, Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
from pydantic import BaseModel, Field
from datetime import datetime

from models import DocumentSummary, ExtractedEvent, LegalRecommendation, LegalAnalysis, CaseStrength
from config import settings

class AIAgentOrchestrator:
    """
    AI Agent orchestrator that manages all AI-powered analysis
    Extracted from the notebook's multi-agent system
    """
    
    def __init__(self):
        # Initialize Azure OpenAI client
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            temperature=0.3
        )
        
        # Initialize parsers
        self.summary_parser = PydanticOutputParser(pydantic_object=DocumentSummary)
        self.event_parser = PydanticOutputParser(pydantic_object=ExtractedEvent)
        
        # Initialize prompts
        self._setup_prompts()
    

    
    def _setup_prompts(self):
        """Setup all prompt templates"""
        
        # Agent 1 - Document Summarizer Prompt
        self.summary_prompt = PromptTemplate(
            template="""You are a legal document analysis expert specializing in Indian law. Analyze the following legal document and provide a comprehensive summary.

Document Content:
{document_content}

Filename: {filename}

Extract the following information:
1. Case number (if any)
2. Parties involved (petitioner/plaintiff vs respondent/defendant)
3. Court name and jurisdiction
4. Document type (petition, order, judgment, etc.)
5. Brief summary of the case
6. Key legal issues identified

Provide your analysis in the following JSON format:
{{
    "case_number": "case number or 'Unknown'",
    "parties": "petitioner vs respondent names",
    "court": "court name and jurisdiction",
    "document_type": "type of legal document",
    "summary": "brief summary of document content",
    "key_legal_issues": ["list", "of", "key", "legal", "issues"],
    "confidence": 0.8
}}
NOTE: The Output strictly be as specified and in a JSON string format, with no extra verbiage or characters 

Be precise and focus on factual information from the document.""",
            input_variables=["document_content", "filename"]
        )

        # Agent 2 - Enhanced Date Extractor Prompt
        self.date_extraction_prompt = PromptTemplate(
            template="""You are a legal timeline extraction expert specializing in Indian law. Extract all chronological events from the provided legal documents.

Combined Document Content:
{combined_content}

IMPORTANT: For any generic roles like "plaintiff", "respondent", "petitioner", "defendant", identify the actual party names and format them as "role (actual_name)". For example:
- "plaintiff (John Doe)" instead of just "plaintiff"
- "respondent (ABC Corporation)" instead of just "respondent"

Extract events with the following details:
1. Date (in YYYY-MM-DD format if possible)
2. Event type (filing, hearing, order, notice, etc.)
3. Description with party identification
4. Parties involved (with actual names)
5. Confidence level (0.0 to 1.0)

Focus on:
- Case filings and petitions
- Court hearings and proceedings
- Orders and judgments
- Notices and summons
- Deadlines and time limits
- Procedural events

Return a JSON array of events. Each event should have this format:
{{
    "date": "YYYY-MM-DD",
    "event_type": "type of event",
    "description": "detailed description",
    "parties_involved": ["party1", "party2"],
    "confidence": 0.8,
    "document_source": "source document name"
}}
NOTE: The Output strictly be as specified and in a JSON string format, with no extra verbiage or characters 

"""
,

            input_variables=["combined_content"]
        )
        
        # Agent 5 - Legal Recommendations Prompt
        self.recommendations_prompt = PromptTemplate(
            template="""You are a senior legal advisor specializing in Indian law. Based on the case analysis, provide actionable legal recommendations.

Case Summary:
{case_summary}

Document Summaries:
{document_summaries}

Timeline Events:
{timeline_events}

Provide comprehensive legal recommendations including:

1. IMMEDIATE ACTIONS (High Priority):
   - Urgent procedural requirements
   - Compliance deadlines
   - Critical next steps

2. STRATEGIC ACTIONS (Medium Priority):
   - Case strengthening measures
   - Evidence collection
   - Legal research areas

3. LONG-TERM CONSIDERATIONS (Low Priority):
   - Future planning
   - Alternative approaches
   - Risk mitigation

4. CASE STRENGTH ASSESSMENT:
   - Overall strength (Strong/Moderate/Weak)
   - Key strengths
   - Potential weaknesses
   - Success probability

5. LEGAL BASIS:
   - Relevant Indian laws and acts
   - Case precedents
   - Procedural requirements

Format your response as JSON:
{{
    "recommendations": [
        {{
            "category": "Procedural",
            "priority": "High",
            "action": "specific action to take",
            "legal_basis": "relevant law/section",
            "timeline": "when to complete",
            "rationale": "why this is important"
        }}
    ],
    "case_strength": {{
        "overall": "Strong/Moderate/Weak",
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "score": 0.7
    }},
    "legal_analysis": "detailed legal analysis text",
    "next_steps": ["step1", "step2", "step3"]
}}
NOTE: The Output strictly be as specified and in a JSON string format, with no extra verbiage or characters 
"""

,

            input_variables=["case_summary", "document_summaries", "timeline_events"]
        )
    
    async def _async_llm_call(self, prompt: str):
        """Make an asynchronous call to the LLM"""
        print("🔄 Making async LLM call...")
        print(f"📏 Prompt length: {len(prompt)} characters")
        try:
            # Create a human message from the prompt
            print("📝 Creating HumanMessage from prompt...")
            message = HumanMessage(content=prompt)
            
            # Make the async call to the LLM
            print("📡 Invoking LLM with prompt...")
            response = await self.llm.ainvoke([message])
            print("✅ LLM response received successfully")
            print(f"📏 Response content length: {len(response.content)} characters")
            
            return response
            
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            raise Exception(f"LLM call failed: {str(e)}")
    async def run_document_summarizer(self, extracted_texts: List[Dict]) -> List[DocumentSummary]:
        """Run Agent 1 - Document Summarizer"""
        print(f"📋 Starting Document Summarizer for {len(extracted_texts)} documents...")
        summaries = []
        
        for i, text_data in enumerate(extracted_texts):
            print(f"📄 Processing document {i+1}/{len(extracted_texts)}: {text_data['filename']}")
            print(f"📏 Document content length: {len(text_data['content'])} characters")
            
            try:
                print("  🔧 Formatting prompt...")
                prompt = self.summary_prompt.format(
                    document_content=text_data['content'][:8000],
                    filename=text_data['filename']
                )
                print(f"  📏 Formatted prompt length: {len(prompt)} characters")
                
                print("  📡 Calling LLM for document summary...")
                response = await self._async_llm_call(prompt)
                
                print("  🔍 Parsing summary response...")
                print("file_name ", text_data['filename'], "llm_response ",response.content)
                summary_data = self._parse_summary_response(response.content)
                
                print("  🏗️ Creating DocumentSummary object...")
                summary = DocumentSummary(
                    case_number=summary_data.get('case_number', 'Unknown'),
                    parties=summary_data.get('parties', 'Unknown'),
                    court=summary_data.get('court', 'Unknown'),
                    document_type=summary_data.get('document_type', 'Unknown'),
                    summary=summary_data.get('summary', text_data['content'][:500]),
                    key_legal_issues=summary_data.get('key_legal_issues', ['Analysis pending']),
                    confidence=summary_data.get('confidence', 0.3)
                )
                summaries.append(summary)
                print(f"  ✅ Document {i+1} processed successfully")
                
            except Exception as e:
                print(f"  ❌ Document {i+1} ({text_data['filename']}) processing failed: {e}")
                print(f"  🔄 Creating fallback summary for document {i+1}")
                
                # Create fallback summary
                fallback_summary = DocumentSummary(
                    case_number='Unknown',
                    parties='Unknown',
                    court='Unknown',
                    document_type='Unknown',
                    summary=f"Processing failed for {text_data['filename']}: {str(e)}",
                    key_legal_issues=[f'Analysis failed: {str(e)[:100]}'],
                    confidence=0.1
                )
                summaries.append(fallback_summary)
                print(f"  ⚠️ Fallback summary created for document {i+1}")
        
        print(f"✅ Document Summarizer completed. Generated {len(summaries)} summaries")
        return summaries
    
    async def run_date_extractor(self, extracted_texts: List[Dict]) -> List[ExtractedEvent]:
        """Run Agent 2 - Enhanced Date Extractor with Party Identification"""
        print(f"📅 Starting Date Extractor for {len(extracted_texts)} documents...")
        
        try:
            print("  🔗 Combining document contents...")
            combined_content = "\n\n".join([
                f"=== {text['filename']} ===\n{text['content']}" 
                for text in extracted_texts
            ])
            print(f"  📏 Combined content length: {len(combined_content)} characters")
            
            print("  🔧 Formatting date extraction prompt...")
            prompt = self.date_extraction_prompt.format(combined_content=combined_content)
            print(f"  📏 Formatted prompt length: {len(prompt)} characters")
            
            print("  📡 Calling LLM for date extraction...")
            response = await self._async_llm_call(prompt)
            
            print("  🔍 Parsing events from response...")
            print( "llm_response ",response.content)
            events = self._parse_events_from_response(response.content)
            
            print(f"  🔄 Deduplicating events...")
            deduplicated_events = self._deduplicate_events(events)
            
            print(f"  ✅ Date extraction completed. Found {len(deduplicated_events)} events")
            return deduplicated_events
            
        except Exception as e:
            print(f"  ❌ Date extraction failed: {e}")
            print(f"  🔄 Returning empty events list due to extraction failure")
            return []  # Return empty list instead of raising exception
    
    async def run_legal_recommendations(self, summaries: List[DocumentSummary], events: List[ExtractedEvent]) -> LegalAnalysis:
        """Run Agent 5 - Legal Recommendations"""
        print(f"⚖️ Starting Legal Recommendations with {len(summaries)} summaries and {len(events)} events...")
        
        try:
            print("  📝 Generating case summary...")
            case_summary = await self.generate_case_summary(summaries, events)
            print(f"  📏 Case summary length: {len(case_summary)} characters")
            
            print("  📋 Preparing document summaries text...")
            document_summaries = "\n\n".join([
                f"Document: {s.document_type}\nCase: {s.case_number}\nParties: {s.parties}\nSummary: {s.summary}"
                for s in summaries
            ])
            
            print("  📅 Preparing timeline events text...")
            timeline_events = "\n".join([
                f"Date: {e.date}, Event: {e.event_type}, Description: {e.description}"
                for e in events
            ]) if events else "No timeline events extracted"
            
            print("  🔧 Formatting recommendations prompt...")
            prompt = self.recommendations_prompt.format(
                case_summary=case_summary,
                document_summaries=document_summaries,
                timeline_events=timeline_events
            )
            print(f"  📏 Formatted prompt length: {len(prompt)} characters")
            
            print("  📡 Calling LLM for legal recommendations...")
            response = await self._async_llm_call(prompt)
            
            print("  🔍 Parsing legal recommendations...")
            analysis = self._parse_legal_recommendations(response.content)
            
            print("  ✅ Legal recommendations completed successfully")
            return analysis
            
        except Exception as e:
            print(f"  ❌ Legal recommendations failed: {e}")
            print(f"  🔄 Creating fallback recommendations due to failure")
            return self._create_fallback_recommendations(str(e))
    
    async def generate_case_summary(self, summaries: List[DocumentSummary], events: List[ExtractedEvent]) -> str:
        """Generate comprehensive case summary"""
        print("📋 Generating comprehensive case summary...")
        print(f"  📊 Processing {len(summaries)} summaries and {len(events)} events...")
        
        if not summaries:
            print("  ❌ No summaries provided for case summary generation")
            raise Exception("No document summaries available for case summary generation")
        
        # Generate basic summary from available data
        summary_parts = []
        summary_parts.append(f"Documents analyzed: {len(summaries)}")
        
        for i, summary in enumerate(summaries):
            summary_parts.append(f"Document {i+1}: {summary.document_type} - {summary.case_number}")
        
        if events:
            summary_parts.append(f"Timeline events: {len(events)}")
        
        case_summary = "\n".join(summary_parts)
        print(f"  ✅ Case summary generated: {len(case_summary)} characters")
        return case_summary

    def _parse_summary_response(self, response_content: str) -> Dict[str, Any]:
        """Parse summary response from LLM"""
        print("  🔍 Parsing summary response...")
        print(f"    📏 Response length: {len(response_content)} characters")
        print(f"    📝 Response preview: {response_content[:200]}...")
        
        if not response_content or response_content.strip() == "":
            print("    ❌ Empty response content")
            print("    🔄 Returning fallback summary data")
            return {
                'case_number': 'Unknown',
                'parties': 'Unknown',
                'court': 'Unknown',
                'document_type': 'Unknown',
                'summary': 'Summary extraction failed - empty response',
                'key_legal_issues': ['Analysis failed - empty response'],
                'confidence': 0.1
            }
        
        try:
            # Clean and parse JSON
            cleaned_content = self._clean_json_response(response_content)
            parsed_data = json.loads(cleaned_content)
            print("    ✅ Successfully parsed as JSON")
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON parsing failed: {e}")
            print(f"    📝 Raw response: {response_content}")
            print(f"    🔄 Returning fallback summary data due to JSON parsing failure")
            return {
                'case_number': 'Unknown',
                'parties': 'Unknown',
                'court': 'Unknown',
                'document_type': 'Unknown',
                'summary': f'Summary extraction failed - JSON parse error: {str(e)[:100]}',
                'key_legal_issues': [f'Analysis failed - JSON error: {str(e)[:50]}'],
                'confidence': 0.1
            }

    def _parse_events_from_response(self, response_content: str) -> List[ExtractedEvent]:
        """Parse events from LLM response"""
        print("  🔍 Parsing events from response...")
        print(f"    📏 Response length: {len(response_content)} characters")
        print(f"    📝 Response preview: {response_content[:200]}...")
        
        if not response_content or response_content.strip() == "":
            print("    ❌ Empty response content for events")
            return []  # Return empty list instead of raising exception
        
        try:
            # Clean and parse JSON
            cleaned_content = self._clean_json_response(response_content)
            events_data = json.loads(cleaned_content)
            
            if not isinstance(events_data, list):
                print(f"    ❌ Expected list, got {type(events_data)}")
                return []  # Return empty list instead of raising exception
            
            events = []
            for i, event_data in enumerate(events_data):
                try:
                    print(f"      🔄 Processing event {i+1}/{len(events_data)}")
                    event = ExtractedEvent(
                        date=event_data.get('date', 'Unknown'),
                        event_type=event_data.get('event_type', 'Unknown'),
                        description=event_data.get('description', ''),
                        parties_involved=event_data.get('parties_involved', []),
                        confidence=event_data.get('confidence', 0.5),
                        document_source=event_data.get('document_source', 'Unknown')
                    )
                    events.append(event)
                except Exception as event_error:
                    print(f"      ❌ Failed to process event {i+1}: {event_error}")
                    print(f"      🔄 Skipping malformed event {i+1}")
                    continue  # Skip this event and continue with others
            
            print(f"    ✅ Successfully parsed {len(events)} events")
            return events
            
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON parsing failed: {e}")
            print(f"    📝 Raw response: {response_content}")
            print(f"    🔄 Returning empty events list due to JSON parsing failure")
            return []  # Return empty list instead of raising exception
        except Exception as e:
            print(f"    ❌ Event parsing error: {e}")
            print(f"    🔄 Returning empty events list due to parsing error")
            return []  # Return empty list instead of raising exception

    def _extract_events_from_text(self, text: str) -> List[ExtractedEvent]:
        """Fallback method to extract events from text"""
        events = []
        lines = text.split("\n")
        
        for line in lines:
            # Look for date patterns
            date_match = re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}", line)
            if date_match:
                event = ExtractedEvent(
                    date=date_match.group(),
                    event_type="Extracted",
                    description=line.strip(),
                    parties_involved=[],
                    confidence=0.5
                )
                events.append(event)
        
        return events[:20]  # Limit to 20 events

    def _deduplicate_events(self, events: List[ExtractedEvent]) -> List[ExtractedEvent]:
        """Remove duplicate events"""
        seen = set()
        deduplicated = []
        
        for event in events:
            event_key = (event.date, event.event_type, event.description)
            if event_key not in seen:
                seen.add(event_key)
                deduplicated.append(event)
        
        # Sort by date
        try:
            deduplicated.sort(key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
        except:
            pass  # Keep original order if date parsing fails
        
        return deduplicated

    def _parse_legal_recommendations(self, response_content: str) -> LegalAnalysis:
        """Parse legal recommendations from LLM response"""
        print("  🔍 Parsing legal recommendations...")
        print(f"    📏 Response length: {len(response_content)} characters")
        print(f"    📝 Response preview: {response_content[:200]}...")
        
        if not response_content or response_content.strip() == "":
            print("    ❌ Empty response content for recommendations")
            print("    🔄 Creating fallback recommendations due to empty response")
            return self._create_fallback_recommendations("Empty response from LLM")
        
        try:
            # Clean and parse JSON
            cleaned_content = self._clean_json_response(response_content)
            data = json.loads(cleaned_content)
            print("    ✅ Successfully parsed recommendations JSON")
            
            # Parse recommendations
            print("    🔄 Processing recommendations...")
            recommendations = []
            for i, rec_data in enumerate(data.get('recommendations', [])):
                try:
                    print(f"      📝 Processing recommendation {i+1}")
                    rec = LegalRecommendation(
                        category=rec_data.get('category', 'General'),
                        priority=rec_data.get('priority', 'Medium'),
                        action=rec_data.get('action', ''),
                        legal_basis=rec_data.get('legal_basis', ''),
                        timeline=rec_data.get('timeline', ''),
                        rationale=rec_data.get('rationale', '')
                    )
                    recommendations.append(rec)
                except Exception as rec_error:
                    print(f"      ❌ Failed to process recommendation {i+1}: {rec_error}")
                    print(f"      🔄 Skipping malformed recommendation {i+1}")
                    continue  # Skip this recommendation and continue with others
            
            # Parse case strength
            print("    🔄 Processing case strength...")
            try:
                strength_data = data.get('case_strength', {})
                case_strength = CaseStrength(
                    overall=strength_data.get('overall', 'Moderate'),
                    strengths=strength_data.get('strengths', []),
                    weaknesses=strength_data.get('weaknesses', []),
                    score=strength_data.get('score', 0.5)
                )
            except Exception as strength_error:
                print(f"    ❌ Failed to process case strength: {strength_error}")
                print(f"    🔄 Using fallback case strength")
                case_strength = CaseStrength(
                    overall='Moderate',
                    strengths=['Assessment incomplete'],
                    weaknesses=['Analysis failed'],
                    score=0.5
                )
            
            print("    🏗️ Creating LegalAnalysis object...")
            analysis = LegalAnalysis(
                recommendations=recommendations,
                case_strength=case_strength,
                legal_analysis=data.get('legal_analysis', 'Analysis incomplete due to parsing issues'),
                next_steps=data.get('next_steps', ['Manual review required'])
            )
            
            print("    ✅ Legal recommendations parsing successful")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON parsing failed: {e}")
            print(f"    📝 Raw response: {response_content}")
            print(f"    🔄 Creating fallback recommendations due to JSON parsing failure")
            return self._create_fallback_recommendations(f"JSON parsing failed: {str(e)}")
        except Exception as e:
            print(f"    ❌ Recommendations parsing error: {e}")
            print(f"    🔄 Creating fallback recommendations due to parsing error")
            return self._create_fallback_recommendations(f"Parsing error: {str(e)}")

    def _create_fallback_recommendations(self, error_msg: str) -> LegalAnalysis:
        """Create fallback recommendations when parsing fails"""
        fallback_rec = LegalRecommendation(
            category="General",
            priority="Medium",
            action="Review case documents and consult legal expert",
            legal_basis="General legal practice",
            timeline="Within 7 days",
            rationale=f"Analysis incomplete due to: {error_msg}"
        )
        
        fallback_strength = CaseStrength(
            overall="Moderate",
            strengths=["Case under review"],
            weaknesses=["Analysis incomplete"],
            score=0.5
        )
        
        return LegalAnalysis(
            recommendations=[fallback_rec],
            case_strength=fallback_strength,
            legal_analysis="Legal analysis could not be completed. Please review manually.",
            next_steps=["Manual review required", "Consult legal expert"]
        )

    def _generate_case_context(self, summaries: List[DocumentSummary]) -> str:
        """Generate case context from summaries"""
        if not summaries:
            return "No case information available"
        
        # Extract common information
        case_numbers = [s.case_number for s in summaries if s.case_number != "Unknown"]
        parties = [s.parties for s in summaries if s.parties != "Unknown"]
        courts = [s.court for s in summaries if s.court != "Unknown"]
        
        context_parts = []
        
        if case_numbers:
            context_parts.append(f"Case: {case_numbers[0]}")
        
        if parties:
            context_parts.append(f"Parties: {parties[0]}")
        
        if courts:
            context_parts.append(f"Court: {courts[0]}")
        
        # Add summary of issues
        all_issues = []
        for s in summaries:
            all_issues.extend(s.key_legal_issues)
        
        if all_issues:
            unique_issues = list(set(all_issues))
            context_parts.append(f"Key Issues: {', '.join(unique_issues[:3])}")
        
        return ". ".join(context_parts) if context_parts else "Case information under review"
    
    def _clean_json_response(self, response_content: str) -> str:
        """Clean response content before JSON parsing"""
        print("    🧹 Cleaning response content...")
        
        # Strip whitespace
        cleaned = response_content.strip()
        
        # Remove common prefixes that LLMs add
        prefixes_to_remove = [
            "json",
            "JSON",
            "```json",
            "```JSON", 
            "```",
            "Here is the JSON:",
            "Here's the JSON:",
            "The JSON is:",
            "JSON:",
            "Response:",
            "Output:",
            "Result:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                print(f"    🧹 Removed prefix: '{prefix}'")
        
        # Remove common suffixes
        suffixes_to_remove = [
            "```",
            "```json",
            "```JSON"
        ]
        
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
                print(f"    🧹 Removed suffix: '{suffix}'")
        
        # Remove any remaining markdown code block markers
        cleaned = re.sub(r'^```[a-zA-Z]*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```$', '', cleaned)
        
        print(f"    🧹 Cleaned content length: {len(cleaned)} characters")
        return cleaned
