import React, { useState } from 'react';
import axios from 'axios';

const DocumentUpload = ({ onUploadSuccess, onUploadStart }) => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);
    onUploadStart();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload/document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      onUploadSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload GP Document
        </h2>
        <p className="text-gray-600">
          Upload investment materials to extract and analyze deal data
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`upload-area ${dragActive ? 'dragover' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="text-gray-500">
            <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          
          <div>
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="mt-2 block text-sm font-medium text-gray-900">
                {file ? file.name : 'Click to upload or drag and drop'}
              </span>
              <span className="mt-1 block text-sm text-gray-500">
                PDF, DOCX, XLSX files up to 10MB
              </span>
            </label>
            <input
              id="file-upload"
              name="file-upload"
              type="file"
              className="sr-only"
              accept=".pdf,.docx,.xlsx,.xls"
              onChange={handleFileSelect}
            />
          </div>
        </div>
      </div>

      {/* Upload Button */}
      {file && (
        <div className="mt-6 text-center">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Processing...' : 'Upload & Analyze'}
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold text-green-800 mb-4">
            ✅ Document Processed Successfully
          </h3>
          <div className="space-y-2">
            <p><strong>Deal ID:</strong> {result.deal_id}</p>
            <p><strong>Confidence Score:</strong> {result.extracted_data.metadata?.confidence_score?.toFixed(2) || 'N/A'}</p>
          </div>
          
          <div className="mt-4">
            <a
              href={`/deals/${result.deal_id}`}
              className="btn-primary"
            >
              View Analysis
            </a>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-8 card border-red-200 bg-red-50">
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            ❌ Upload Failed
          </h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
