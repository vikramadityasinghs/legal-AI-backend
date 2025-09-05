// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Configure marked for better markdown parsing
if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true,
        gfm: true,
        sanitize: false,
        smartLists: true,
        smartypants: true
    });
}

// Global state
let currentJobId = null;
let selectedFiles = [];
let analysisResults = null;
let availableCases = [];

// Page Navigation Functions
function showUploadFlow() {
    hideAllPages();
    showElement('uploadFlow');
}

function showExistingCases() {
    hideAllPages();
    showElement('existingCases');
    loadAvailableCases();
}

function goBackToMenu() {
    hideAllPages();
    showElement('mainMenu');
}

function goBackToExistingCases() {
    hideAllPages();
    showElement('existingCases');
}

function hideAllPages() {
    const pages = ['mainMenu', 'uploadFlow', 'existingCases', 'caseResults'];
    pages.forEach(pageId => {
        hideElement(pageId);
    });
}

// Utility functions
function showElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('hidden');
    }
}

function hideElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

// File Upload Functions
function startAnalysis() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files.length) {
        alert('Please select files first');
        return;
    }

    hideElement('uploadSection');
    showElement('progressSection');
    
    // Implement upload logic here
    uploadFiles(fileInput.files);
}

async function uploadFiles(files) {
    try {
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        updateProgress(10, 'Uploading files...');

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const result = await response.json();
        console.log('Upload response:', result); // Debug logging
        currentJobId = result.job_id;
        
        updateProgress(25, 'Files uploaded successfully');
        
        // If cached result is available, start polling immediately
        if (result.cached || result.instant_results) {
            console.log('Found cached results, starting immediate polling');
            updateProgress(50, 'Found cached results, loading...');
            pollJobStatus();
        } else {
            console.log('No cached results, starting fresh analysis');
            // Start analysis for new documents
            updateProgress(30, 'Starting analysis...');
            await startDocumentAnalysis();
        }

    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed: ' + error.message);
        resetUpload();
    }
}

async function pollJobStatus() {
    if (!currentJobId) return;

    try {
        console.log('Polling status for job:', currentJobId);
        // First check status
        const statusResponse = await fetch(`${API_BASE_URL}/status/${currentJobId}`);
        const statusData = await statusResponse.json();
        console.log('Status response:', statusData);

        updateProgress(statusData.progress || 0, statusData.current_step || 'Processing...');

        if (statusData.status === 'completed') {
            console.log('Job completed, fetching full results');
            // Now get the full results
            const resultsResponse = await fetch(`${API_BASE_URL}/results/${currentJobId}`);
            const resultsData = await resultsResponse.json();
            console.log('Results response:', resultsData);
            analysisResults = resultsData;
            showResults();
        } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Analysis failed');
        } else {
            console.log('Job still in progress, continuing to poll...');
            // Continue polling for status updates
            setTimeout(pollJobStatus, 2000);
        }
    } catch (error) {
        console.error('Polling error:', error);
        alert('Analysis failed: ' + error.message);
        resetUpload();
    }
}

function updateProgress(percentage, text) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const currentStep = document.getElementById('currentStep');

    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    if (progressText) {
        progressText.textContent = `${Math.round(percentage)}%`;
    }
    if (currentStep) {
        currentStep.textContent = text;
    }
}

function showResults() {
    hideElement('progressSection');
    showElement('resultsSection');
    
    // Update downloads section
    updateDownloadsSection(analysisResults.downloads);
    
    // Update case summary
    updateCaseSummary(analysisResults.case_summary);
}

function resetUpload() {
    hideElement('progressSection');
    hideElement('resultsSection');
    showElement('uploadSection');
    currentJobId = null;
    analysisResults = null;
    updateProgress(0, 'Ready to start');
}

// Existing Cases Functions
async function loadAvailableCases() {
    try {
        const response = await fetch(`${API_BASE_URL}/cache/list`);
        const data = await response.json();
        
        // Convert the API response format to what displayCasesList expects
        const cases = {};
        if (data.recent_cases && Array.isArray(data.recent_cases)) {
            data.recent_cases.forEach(caseInfo => {
                cases[caseInfo.case_id] = {
                    cached_at: caseInfo.cached_at,
                    last_accessed: caseInfo.last_accessed,
                    case_names: caseInfo.case_names
                };
            });
        }
        
        displayCasesList(cases);
        
    } catch (error) {
        console.error('Error loading cases:', error);
        displayCasesError();
    }
}

function displayCasesList(cases) {
    const casesList = document.getElementById('casesList');
    
    if (Object.keys(cases).length === 0) {
        casesList.innerHTML = `
            <div class="text-center py-8">
                <div class="text-4xl text-gray-400 mb-4">
                    <i class="fas fa-folder-open"></i>
                </div>
                <p class="text-gray-600">No cached cases available</p>
            </div>
        `;
        return;
    }

    const casesHtml = Object.entries(cases).map(([caseId, caseInfo]) => `
        <div class="case-card card p-6" onclick="selectCase('${caseId}')">
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">
                        ${formatCaseTitle(caseId)}
                    </h3>
                    <div class="text-sm text-gray-600 space-y-1">
                        <div><i class="fas fa-calendar mr-2"></i>Added: ${formatDate(caseInfo.cached_at)}</div>
                        <div><i class="fas fa-file-alt mr-2"></i>Case ID: ${caseId}</div>
                    </div>
                </div>
                <div class="text-3xl text-green-600">
                    <i class="fas fa-chevron-right"></i>
                </div>
            </div>
        </div>
    `).join('');

    casesList.innerHTML = casesHtml;
}

function displayCasesError() {
    const casesList = document.getElementById('casesList');
    casesList.innerHTML = `
        <div class="text-center py-8">
            <div class="text-4xl text-red-400 mb-4">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <p class="text-red-600">Error loading cases</p>
            <button onclick="loadAvailableCases()" class="btn-primary mt-4">
                <i class="fas fa-redo mr-2"></i>Try Again
            </button>
        </div>
    `;
}

async function selectCase(caseId) {
    try {
        showElement('caseResults');
        hideElement('existingCases');
        
        // Update case title
        document.getElementById('caseTitle').textContent = formatCaseTitle(caseId);
        
        // Show loading state
        document.getElementById('downloadButtonsResults').innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>';
        document.getElementById('summaryContent').innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>';
        
        // Fetch case data
        const response = await fetch(`${API_BASE_URL}/cache/case/${caseId}`);
        if (!response.ok) {
            throw new Error('Failed to load case');
        }
        
        const caseData = await response.json();
        
        // Update downloads
        updateDownloadsSectionResults(caseData.downloads);
        
        // Update summary
        updateSummaryContent(caseData.case_summary);
        
    } catch (error) {
        console.error('Error loading case:', error);
        alert('Error loading case: ' + error.message);
        goBackToExistingCases();
    }
}

// Download Functions
function updateDownloadsSection(downloads) {
    const downloadsDiv = document.getElementById('downloadButtons');
    if (!downloadsDiv) return;
    
    if (!downloads) {
        downloadsDiv.innerHTML = '<p class="text-gray-500">No downloads available</p>';
        return;
    }
    
    let downloadButtons = '';
    
    // Excel download button
    if (downloads.excel_available && downloads.excel_url) {
        downloadButtons += `
            <button onclick="downloadFile('${downloads.excel_url}', 'excel')" 
                    class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center">
                <i class="fas fa-file-excel mr-2"></i>
                Download Excel Report
            </button>
        `;
    }
    
    // JSON download button
    if (downloads.json_url) {
        downloadButtons += `
            <button onclick="downloadFile('${downloads.json_url}', 'json')" 
                    class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center ml-2">
                <i class="fas fa-file-code mr-2"></i>
                Download JSON Data
            </button>
        `;
    }
    
    downloadsDiv.innerHTML = downloadButtons || '<p class="text-gray-500">No downloads available</p>';
}

function updateDownloadsSectionResults(downloads) {
    const downloadsDiv = document.getElementById('downloadButtonsResults');
    if (!downloadsDiv) return;
    
    if (!downloads) {
        downloadsDiv.innerHTML = '<p class="text-gray-500">No downloads available</p>';
        return;
    }
    
    let downloadButtons = '';
    
    // Excel download button
    if (downloads.excel_available && downloads.excel_url) {
        downloadButtons += `
            <button onclick="downloadFile('${downloads.excel_url}', 'excel')" 
                    class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center mr-2 mb-2">
                <i class="fas fa-file-excel mr-2"></i>
                Download Excel Report
            </button>
        `;
    }
    
    // JSON download button
    if (downloads.json_url) {
        downloadButtons += `
            <button onclick="downloadFile('${downloads.json_url}', 'json')" 
                    class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center mr-2 mb-2">
                <i class="fas fa-file-code mr-2"></i>
                Download JSON Data
            </button>
        `;
    }
    
    downloadsDiv.innerHTML = downloadButtons || '<p class="text-gray-500">No downloads available</p>';
}

async function downloadFile(url, type) {
    try {
        const response = await fetch(`${API_BASE_URL}${url}`);
        
        if (!response.ok) {
            throw new Error(`Failed to download ${type} file`);
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        
        // Get filename from Content-Disposition header or create one
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `legal_analysis.${type === 'excel' ? 'xlsx' : 'json'}`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="(.+)"/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
    } catch (error) {
        console.error('Download error:', error);
        alert('Download failed: ' + error.message);
    }
}

// Summary Functions
function updateCaseSummary(summary) {
    const caseSummaryDiv = document.getElementById('caseSummary');
    if (!caseSummaryDiv) return;
    
    if (summary) {
        caseSummaryDiv.innerHTML = `
            <div class="bg-gray-50 p-6 rounded-lg">
                <div class="prose max-w-none">
                    <pre class="whitespace-pre-wrap font-sans text-gray-700">${summary}</pre>
                </div>
            </div>
        `;
    } else {
        caseSummaryDiv.innerHTML = '<p class="text-gray-500">No case summary available</p>';
    }
}

function updateSummaryContent(summary) {
    const summaryContent = document.getElementById('summaryContent');
    if (!summaryContent) return;
    
    if (summary) {
        // Parse markdown and render as HTML
        const markdownHtml = marked.parse(summary);
        summaryContent.innerHTML = `
            <div class="bg-gray-50 p-6 rounded-lg">
                <div class="markdown-content">
                    ${markdownHtml}
                </div>
            </div>
        `;
    } else {
        summaryContent.innerHTML = '<p class="text-gray-500">No case summary available</p>';
    }
}

// Utility Functions
function formatCaseTitle(caseId) {
    return caseId.replace(/_/g, ' ')
                 .replace(/\b\w/g, l => l.toUpperCase());
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    try {
        return new Date(dateString).toLocaleDateString();
    } catch {
        return dateString;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Legal Document Analysis System initialized');
    
    // Set up file input handler
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const files = event.target.files;
            if (files.length > 0) {
                displaySelectedFiles(files);
            }
        });
    }
});

function displaySelectedFiles(files) {
    const selectedFilesDiv = document.getElementById('selectedFiles');
    const uploadButton = document.getElementById('uploadButton');
    
    if (files.length === 0) {
        hideElement('selectedFiles');
        hideElement('uploadButton');
        return;
    }
    
    const filesHtml = Array.from(files).map(file => `
        <div class="flex items-center justify-between bg-gray-100 p-3 rounded">
            <div class="flex items-center">
                <i class="fas fa-file text-blue-600 mr-2"></i>
                <span class="text-sm font-medium">${file.name}</span>
            </div>
            <span class="text-xs text-gray-500">${(file.size / 1024).toFixed(1)} KB</span>
        </div>
    `).join('');
    
    selectedFilesDiv.innerHTML = `
        <h4 class="text-md font-semibold text-gray-800 mb-3">Selected Files (${files.length}):</h4>
        <div class="space-y-2">
            ${filesHtml}
        </div>
    `;
    
    showElement('selectedFiles');
    showElement('uploadButton');
}

async function startDocumentAnalysis() {
    if (!currentJobId) {
        throw new Error('No job ID available');
    }

    try {
        console.log('Starting analysis for job:', currentJobId);
        updateProgress(35, 'Initiating document analysis...');
        
        const response = await fetch(`${API_BASE_URL}/analyze/${currentJobId}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Analysis start failed:', response.status, errorText);
            throw new Error(`Failed to start analysis: ${response.status} ${errorText}`);
        }

        const result = await response.json();
        console.log('Analysis start response:', result);
        
        if (result.status === 'processing') {
            updateProgress(40, 'Analysis started, processing documents...');
            // Start polling for status updates
            pollJobStatus();
        } else if (result.status === 'completed') {
            // Already completed (probably cached)
            updateProgress(100, 'Analysis completed');
            pollJobStatus();
        } else {
            throw new Error(`Unexpected analysis status: ${result.status}`);
        }

    } catch (error) {
        console.error('Analysis start error:', error);
        throw error;
    }
}
