import React, { useState } from 'react';
import { Upload, X, CheckCircle, AlertCircle, FileText, Loader2 } from 'lucide-react';
import { uploadDocument, checkJobStatus } from '../services/api';

export default function IngestModal({ isOpen, onClose, onIngestSuccess }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState(null); // { type: 'info'|'success'|'error', text: '' }
  const [jobInfo, setJobInfo] = useState(null);

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setStatus({ type: 'info', text: 'Uploading PDF to server...' });

    try {
      const data = await uploadDocument(file);
      setJobInfo(data);
      setStatus({ type: 'info', text: `Extraction job started (ID: ${data.job_id}). Processing text, tables, and images...` });

      // Poll job status every 2 seconds
      const pollInterval = setInterval(async () => {
        try {
          const res = await checkJobStatus(data.job_id);
          setJobInfo(res);

          if (res.status === 'completed') {
            clearInterval(pollInterval);
            setIsUploading(false);
            setStatus({
              type: 'success',
              text: `Ingestion complete! Successfully stored ${res.chunks_stored} multimodal chunks in Pinecone.`
            });
            if (onIngestSuccess) onIngestSuccess(res);
          } else if (res.status === 'failed') {
            clearInterval(pollInterval);
            setIsUploading(false);
            setStatus({ type: 'error', text: res.error || 'Ingestion failed.' });
          }
        } catch {
          // Keep polling
        }
      }, 2500);

    } catch (err) {
      setIsUploading(false);
      setStatus({ type: 'error', text: err.message || 'Upload failed' });
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-med-950/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-md bg-chalk-50 border border-chalk-300 rounded-3xl p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full text-chalk-500 hover:text-med-950 hover:bg-chalk-200 transition"
        >
          <X size={18} />
        </button>

        <div className="flex items-center gap-2.5 mb-2">
          <div className="w-8 h-8 rounded-xl bg-med-700 text-white flex items-center justify-center shadow-sm">
            <Upload size={16} />
          </div>
          <div>
            <h3 className="font-bold text-base text-med-950">Ingest PDF Document</h3>
            <p className="text-xs text-chalk-500">Multimodal extraction: text, tables & diagrams</p>
          </div>
        </div>

        {/* Drop Area */}
        <div className="my-5 border-2 border-dashed border-chalk-400/80 hover:border-med-600 rounded-2xl p-6 text-center bg-chalk-100/60 transition">
          <input
            type="file"
            id="pdfDrop"
            accept="application/pdf"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setFile(e.target.files[0]);
                setStatus(null);
              }
            }}
            className="hidden"
          />
          <label htmlFor="pdfDrop" className="cursor-pointer flex flex-col items-center">
            <FileText size={32} className="text-med-600 mb-2" />
            <span className="text-sm font-semibold text-med-950">
              {file ? file.name : "Choose a PDF file to upload"}
            </span>
            <span className="text-xs text-chalk-500 mt-1">Supports corporate reports, resumes, research papers</span>
          </label>
        </div>

        {/* Status Indicator */}
        {status && (
          <div className={`p-3 rounded-xl text-xs mb-4 flex items-start gap-2 ${
            status.type === 'success'
              ? 'bg-med-50 border border-med-200 text-med-900'
              : status.type === 'error'
              ? 'bg-cognac-50 border border-cognac-200 text-cognac-900'
              : 'bg-chalk-200 border border-chalk-300 text-med-900'
          }`}>
            {status.type === 'success' ? (
              <CheckCircle size={15} className="text-med-600 flex-shrink-0 mt-0.5" />
            ) : status.type === 'error' ? (
              <AlertCircle size={15} className="text-cognac-600 flex-shrink-0 mt-0.5" />
            ) : (
              <Loader2 size={15} className="text-med-600 animate-spin flex-shrink-0 mt-0.5" />
            )}
            <span className="leading-relaxed">{status.text}</span>
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-2">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-xl text-xs font-semibold text-chalk-800 bg-chalk-200 hover:bg-chalk-300 transition"
          >
            Close
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className={`flex-1 py-2 rounded-xl text-xs font-semibold text-white transition ${
              !file || isUploading
                ? 'bg-chalk-400 cursor-not-allowed'
                : 'bg-med-700 hover:bg-med-800 shadow-sm'
            }`}
          >
            {isUploading ? 'Processing...' : 'Start Ingestion'}
          </button>
        </div>
      </div>
    </div>
  );
}
