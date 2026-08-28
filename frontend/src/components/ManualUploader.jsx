import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';

export function ManualUploader({ onUploadSuccess, onClose }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type === 'application/pdf') {
      setFile(selected);
      setError(null);
    } else {
      setError('Please select a valid PDF file.');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    try {
      await onUploadSuccess(file);
      setIsUploading(false);
      onClose();
    } catch (err) {
      setIsUploading(false);
      setError(err.response?.data?.detail || 'Failed to upload and parse laboratory manual PDF.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold text-white">Upload Laboratory Manual</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-sm">✕</button>
        </div>

        {/* Drag & drop container */}
        <div className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-6 text-center transition bg-slate-950/40">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            id="pdf-upload"
          />
          <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400">
              <Upload className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">Click to browse or drop PDF manual</p>
              <p className="text-xs text-slate-500 mt-1">Supports standard lab manual PDFs (Max 50MB)</p>
            </div>
          </label>
        </div>

        {/* Selected file preview */}
        {file && (
          <div className="mt-4 p-3 bg-slate-800 rounded-lg flex items-center justify-between border border-slate-700">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-blue-400" />
              <div>
                <p className="text-xs font-semibold text-slate-200 truncate max-w-[200px]">{file.name}</p>
                <p className="text-[10px] text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mt-4 p-3 bg-rose-950/50 border border-rose-800 text-rose-300 rounded-lg text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold px-5 py-2 rounded-lg transition"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing & Indexing...</span>
              </>
            ) : (
              <span>Start Analysis</span>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
