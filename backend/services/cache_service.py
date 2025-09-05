"""
Case Caching Service for Legal Document Analysis System
Provides intelligent caching based on case names and IDs with cross-referencing
"""

import json
import hashlib
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class CachedCase:
    """Represents a cached case analysis"""
    case_id: str
    case_names: List[str]  # Multiple names/variations for the same case
    case_numbers: List[str]  # Legal case numbers (MC 123 of 2024, etc.)
    parties: List[str]  # Key parties involved
    court_name: str
    file_hash: str  # Hash of the original files
    analysis_result: Dict[str, Any]
    cached_at: datetime
    last_accessed: datetime
    access_count: int
    file_names: List[str]  # Original file names
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['cached_at'] = self.cached_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedCase':
        """Create from dictionary"""
        data['cached_at'] = datetime.fromisoformat(data['cached_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

class CaseCacheService:
    """Service for caching and retrieving legal case analyses"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "case_cache.json"
        self.cache_index_file = self.cache_dir / "cache_index.json"
        
        # Load existing cache
        self.cached_cases: Dict[str, CachedCase] = self._load_cache()
        self.name_index: Dict[str, str] = self._load_name_index()
        
        # Initialize with existing cached case if available
        self._initialize_with_existing_data()
    
    def _load_cache(self) -> Dict[str, CachedCase]:
        """Load cached cases from file"""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    case_id: CachedCase.from_dict(case_data) 
                    for case_id, case_data in data.items()
                }
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}
    
    def _load_name_index(self) -> Dict[str, str]:
        """Load name to case ID mapping"""
        if not self.cache_index_file.exists():
            return {}
        
        try:
            with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading name index: {e}")
            return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            data = {
                case_id: case.to_dict() 
                for case_id, case in self.cached_cases.items()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _save_name_index(self):
        """Save name index to file"""
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.name_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving name index: {e}")
    
    def _initialize_with_existing_data(self):
        """Initialize cache with existing legal_analysis_results file"""
        existing_file = Path("/Users/averm234/Library/CloudStorage/OneDrive-UHG/Documents/GitHub/atm-ml-cpml-eni-claims-business-apis/legal_analysis_results_20250815_005809.json")
        
        if existing_file.exists() and not self.cached_cases:
            try:
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                # Extract case information from existing data
                case_names = ["Manjunath vs Ashwini", "Shri. Manjunath Basavaraj Singai vs Smt. Ashwini Manjunath Singai"]
                case_numbers = ["MC 123 of 2024", "MC 101 of 2023", "MC 31 of 2023", "CRL MSC 292 of 2023", "WP 203111 of 2023"]
                parties = ["Shri. Manjunath Basavaraj Singai", "Smt. Ashwini Manjunath Singai"]
                court_name = "Family Court, Raichur"
                
                # Create cached case with transformed format for compatibility
                case_id = "manjunath_ashwini_matrimonial_2023_2024"
                file_hash = self._generate_content_hash(str(existing_data))
                
                # Transform the existing data format to match current API expectations
                transformed_data = {
                    "job_id": case_id,
                    "case_summary": existing_data.get('agent_outputs', {}).get('agent1_summary', {}).get('content', ''),
                    "document_summaries": [],  # Would need to parse from agent outputs
                    "events": [],  # Would need to parse from agent outputs  
                    "recommendations": [],  # Would need to parse from agent outputs
                    "extraction_stats": {"total_documents": 24, "successful_extractions": 24},
                    "completed_at": "2025-08-15T00:58:09.551588",
                    "original_data": existing_data  # Keep original for reference
                }
                
                cached_case = CachedCase(
                    case_id=case_id,
                    case_names=case_names,
                    case_numbers=case_numbers,
                    parties=parties,
                    court_name=court_name,
                    file_hash=file_hash,
                    analysis_result=transformed_data,
                    cached_at=datetime.fromisoformat("2025-08-15T00:58:09.551588"),
                    last_accessed=datetime.now(),
                    access_count=0,
                    file_names=["Manjunath_vs_Ashwini_matrimonial_documents.pdf"]
                )
                
                self.cached_cases[case_id] = cached_case
                
                # Update name index
                for name in case_names:
                    self.name_index[self._normalize_name(name)] = case_id
                for number in case_numbers:
                    self.name_index[self._normalize_name(number)] = case_id
                for party in parties:
                    self.name_index[self._normalize_name(party)] = case_id
                
                self._save_cache()
                self._save_name_index()
                
                print(f"Initialized cache with existing case: {case_id}")
                
            except Exception as e:
                print(f"Error initializing with existing data: {e}")
    
    def _normalize_name(self, name: str) -> str:
        """Normalize case name for consistent matching"""
        # Convert to lowercase, remove special characters, normalize whitespace
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _generate_file_hash(self, files: List[Any]) -> str:
        """Generate hash from uploaded files"""
        hasher = hashlib.md5()
        for file in files:
            if hasattr(file, 'read'):
                content = file.read()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                hasher.update(content)
                file.seek(0)  # Reset file pointer
            elif isinstance(file, (str, bytes)):
                if isinstance(file, str):
                    file = file.encode('utf-8')
                hasher.update(file)
        return hasher.hexdigest()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash from content string"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _extract_case_info_from_analysis(self, analysis_result: Dict[str, Any]) -> Tuple[List[str], List[str], List[str], str]:
        """Extract case information from analysis result"""
        case_names = []
        case_numbers = []
        parties = []
        court_name = ""
        
        # Extract from document summaries
        if 'agent_outputs' in analysis_result:
            summaries = analysis_result['agent_outputs'].get('agent1_summary', {})
            if 'metadata' in summaries and 'document_summaries' in summaries['metadata']:
                for doc in summaries['metadata']['document_summaries']:
                    case_numbers.extend(doc.get('case_numbers', []))
                    parties.extend(doc.get('parties_petitioner', []))
                    parties.extend(doc.get('parties_respondent', []))
                    if doc.get('court_name'):
                        court_name = doc['court_name']
        
        # Extract from main content
        if 'document_summary' in analysis_result:
            summary = analysis_result['document_summary']
            if 'case_title' in summary and summary['case_title']:
                case_names.append(summary['case_title'])
            if 'case_number' in summary and summary['case_number']:
                case_numbers.append(summary['case_number'])
            if 'court' in summary and summary['court']:
                court_name = summary['court']
            if 'parties' in summary:
                for party in summary['parties']:
                    if isinstance(party, dict) and 'name' in party:
                        parties.append(party['name'])
                    elif isinstance(party, str):
                        parties.append(party)
        
        # Remove duplicates
        case_names = list(set(case_names))
        case_numbers = list(set(case_numbers))
        parties = list(set(parties))
        
        return case_names, case_numbers, parties, court_name
    
    def check_cache_by_files(self, files: List[Any]) -> Optional[Dict[str, Any]]:
        """Check if analysis exists in cache based on file hash"""
        file_hash = self._generate_file_hash(files)
        
        for case in self.cached_cases.values():
            if case.file_hash == file_hash:
                # Update access stats
                case.last_accessed = datetime.now()
                case.access_count += 1
                self._save_cache()
                
                print(f"Cache hit by file hash for case: {case.case_id}")
                return case.analysis_result
        
        return None
    
    def check_cache_by_content(self, file_names: List[str], case_indicators: List[str] = None) -> Optional[Dict[str, Any]]:
        """Check if analysis exists in cache based on case names, parties, or case numbers"""
        
        # Prepare search terms
        search_terms = []
        
        # Add file names and extract key terms from them
        for name in file_names:
            # Add full normalized name
            search_terms.append(self._normalize_name(name))
            
            # Extract key terms from filename
            # Remove common file extensions and patterns
            clean_name = name.lower()
            clean_name = re.sub(r'\.(pdf|jpg|jpeg|png)$', '', clean_name)
            clean_name = re.sub(r'case\s*status', '', clean_name)
            
            # Extract case numbers (e.g., "WP 203111 OF 2023")
            case_number_matches = re.findall(r'([a-z]{1,4}\s*\d+\s*of\s*\d{4})', clean_name, re.IGNORECASE)
            for match in case_number_matches:
                search_terms.append(self._normalize_name(match))
            
            # Extract potential party names (words before 'v' or 'vs')
            party_matches = re.findall(r'([a-z]+)\s*v[s]?\s*([a-z]+)', clean_name, re.IGNORECASE)
            for match in party_matches:
                search_terms.append(self._normalize_name(match[0]))  # First party
                search_terms.append(self._normalize_name(match[1]))  # Second party
                search_terms.append(self._normalize_name(f"{match[0]} vs {match[1]}"))  # Combined
            
            # Split filename into words and add significant ones
            words = re.findall(r'[a-z]{3,}', clean_name, re.IGNORECASE)
            for word in words:
                if len(word) > 3:  # Only significant words
                    search_terms.append(self._normalize_name(word))
        
        # Add case indicators if provided
        if case_indicators:
            for indicator in case_indicators:
                search_terms.append(self._normalize_name(indicator))
        
        print(f"Cache search terms: {search_terms}")  # Debug logging
        
        # Search in name index
        for term in search_terms:
            if term in self.name_index:
                case_id = self.name_index[term]
                if case_id in self.cached_cases:
                    case = self.cached_cases[case_id]
                    
                    # Update access stats
                    case.last_accessed = datetime.now()
                    case.access_count += 1
                    self._save_cache()
                    
                    print(f"Cache hit by content match for case: {case_id} (matched term: {term})")
                    return case.analysis_result
        
        # Fuzzy matching for partial matches
        for case in self.cached_cases.values():
            # Check case names
            for case_name in case.case_names:
                normalized_case_name = self._normalize_name(case_name)
                for term in search_terms:
                    if term in normalized_case_name or normalized_case_name in term:
                        if len(term) > 5 and len(normalized_case_name) > 5:  # Avoid short false matches
                            case.last_accessed = datetime.now()
                            case.access_count += 1
                            self._save_cache()
                            
                            print(f"Cache hit by fuzzy match for case: {case.case_id} (matched: {case_name} ~ {term})")
                            return case.analysis_result
            
            # Check parties
            for party in case.parties:
                normalized_party = self._normalize_name(party)
                for term in search_terms:
                    if term in normalized_party or normalized_party in term:
                        if len(term) > 5 and len(normalized_party) > 5:
                            case.last_accessed = datetime.now()
                            case.access_count += 1
                            self._save_cache()
                            
                            print(f"Cache hit by party match for case: {case.case_id} (matched: {party} ~ {term})")
                            return case.analysis_result
        
        return None
    
    def cache_analysis(self, files: List[Any], file_names: List[str], analysis_result: Dict[str, Any]) -> str:
        """Cache a new analysis result"""
        
        # Extract case information
        case_names, case_numbers, parties, court_name = self._extract_case_info_from_analysis(analysis_result)
        
        # Generate case ID
        if case_names:
            base_name = case_names[0]
        elif parties:
            base_name = " vs ".join(parties[:2])
        else:
            base_name = "unknown_case"
        
        case_id = self._normalize_name(base_name).replace(' ', '_') + f"_{datetime.now().strftime('%Y%m%d')}"
        
        # Ensure unique case ID
        counter = 1
        original_case_id = case_id
        while case_id in self.cached_cases:
            case_id = f"{original_case_id}_{counter}"
            counter += 1
        
        # Create cached case
        file_hash = self._generate_file_hash(files)
        
        cached_case = CachedCase(
            case_id=case_id,
            case_names=case_names,
            case_numbers=case_numbers,
            parties=parties,
            court_name=court_name,
            file_hash=file_hash,
            analysis_result=analysis_result,
            cached_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            file_names=file_names
        )
        
        # Store in cache
        self.cached_cases[case_id] = cached_case
        
        # Update name index
        all_names = case_names + case_numbers + parties + file_names
        for name in all_names:
            if name and name.strip():
                self.name_index[self._normalize_name(name)] = case_id
        
        # Save to disk
        self._save_cache()
        self._save_name_index()
        
        print(f"Cached new analysis for case: {case_id}")
        return case_id
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_cases = len(self.cached_cases)
        total_access_count = sum(case.access_count for case in self.cached_cases.values())
        
        # Most accessed cases
        most_accessed = sorted(
            self.cached_cases.values(), 
            key=lambda x: x.access_count, 
            reverse=True
        )[:5]
        
        # Recent cases
        recent_cases = sorted(
            self.cached_cases.values(), 
            key=lambda x: x.last_accessed, 
            reverse=True
        )[:5]
        
        return {
            "total_cached_cases": total_cases,
            "total_access_count": total_access_count,
            "most_accessed_cases": [
                {
                    "case_id": case.case_id,
                    "case_names": case.case_names,
                    "access_count": case.access_count,
                    "last_accessed": case.last_accessed.isoformat()
                }
                for case in most_accessed
            ],
            "recent_cases": [
                {
                    "case_id": case.case_id,
                    "case_names": case.case_names,
                    "cached_at": case.cached_at.isoformat(),
                    "last_accessed": case.last_accessed.isoformat()
                }
                for case in recent_cases
            ],
            "cache_size_mb": self._get_cache_size_mb()
        }
    
    def _get_cache_size_mb(self) -> float:
        """Get total cache size in MB"""
        total_size = 0
        if self.cache_file.exists():
            total_size += self.cache_file.stat().st_size
        if self.cache_index_file.exists():
            total_size += self.cache_index_file.stat().st_size
        return round(total_size / (1024 * 1024), 2)
    
    def clear_old_cache(self, days: int = 30):
        """Clear cache entries older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for case_id, case in self.cached_cases.items():
            if case.last_accessed < cutoff_date:
                to_remove.append(case_id)
        
        for case_id in to_remove:
            # Remove from name index
            case = self.cached_cases[case_id]
            for name in case.case_names + case.case_numbers + case.parties + case.file_names:
                normalized = self._normalize_name(name)
                if normalized in self.name_index and self.name_index[normalized] == case_id:
                    del self.name_index[normalized]
            
            # Remove from cache
            del self.cached_cases[case_id]
        
        if to_remove:
            self._save_cache()
            self._save_name_index()
            print(f"Removed {len(to_remove)} old cache entries")
        
        return len(to_remove)
    
    def search_cached_cases(self, query: str) -> List[Dict[str, Any]]:
        """Search for cached cases by query"""
        normalized_query = self._normalize_name(query)
        results = []
        
        for case in self.cached_cases.values():
            # Check if query matches any case information
            searchable_text = " ".join([
                " ".join(case.case_names),
                " ".join(case.case_numbers),
                " ".join(case.parties),
                case.court_name,
                " ".join(case.file_names)
            ]).lower()
            
            if normalized_query in searchable_text:
                results.append({
                    "case_id": case.case_id,
                    "case_names": case.case_names,
                    "case_numbers": case.case_numbers,
                    "parties": case.parties,
                    "court_name": case.court_name,
                    "cached_at": case.cached_at.isoformat(),
                    "last_accessed": case.last_accessed.isoformat(),
                    "access_count": case.access_count
                })
        
        return results
    
    def get_cached_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get cached case analysis result by case ID"""
        if case_id in self.cached_cases:
            case = self.cached_cases[case_id]
            
            # Update access stats
            case.last_accessed = datetime.now()
            case.access_count += 1
            self._save_cache()
            
            print(f"Retrieved cached case by ID: {case_id}")
            return case.analysis_result
        
        return None
