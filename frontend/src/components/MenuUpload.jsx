import React, { useState, useRef } from 'react';
import { uploadMenu } from '../services/api';
import { UploadCloud, CheckCircle, Loader2, AlertCircle } from 'lucide-react';

export default function MenuUpload({ userId, onUploadSuccess }) {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('idle'); // idle, uploading, success, error
    const [errorMsg, setErrorMsg] = useState('');
    const fileInput = useRef(null);

    const handleUpload = async () => {
        if (!file) return;
        setStatus('uploading');
        try {
            await uploadMenu(file, userId);
            setStatus('success');
            onUploadSuccess(); // triggers the next stage in App
        } catch (err) {
            setStatus('error');
            setErrorMsg(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div className="bg-[#18181b] border border-white/10 rounded-2xl p-8 mb-8 shadow-xl">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span>
                Menu Ingestion
            </h2>
            <p className="text-slate-400 mb-6 text-sm">Upload a PDF or TXT file of the restaurant's menu.</p>

            <div
                onClick={() => status !== 'uploading' && fileInput.current.click()}
                className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors ${file ? 'border-indigo-500 bg-indigo-500/5' : 'border-white/10 hover:border-indigo-500/30'}`}
            >
                <input
                    type="file"
                    ref={fileInput}
                    className="hidden"
                    accept=".pdf,.txt"
                    onChange={e => {
                        setFile(e.target.files[0]);
                        setStatus('idle');
                    }}
                />

                {status === 'success' ? (
                    <div className="flex flex-col items-center text-emerald-500">
                        <CheckCircle size={40} className="mb-3" />
                        <span className="font-bold">Upload Complete</span>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-indigo-400">
                        <UploadCloud size={40} className="mb-3" />
                        <span className="font-bold">{file ? file.name : 'Select file to upload'}</span>
                    </div>
                )}
            </div>

            {status === 'error' && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-center gap-2 text-sm">
                    <AlertCircle size={16} /> {errorMsg}
                </div>
            )}

            <button
                onClick={handleUpload}
                disabled={!file || status === 'uploading' || status === 'success'}
                className="mt-6 w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl font-semibold transition-colors flex justify-center items-center gap-2"
            >
                {status === 'uploading' ? <Loader2 className="animate-spin" size={20} /> : null}
                Upload Document
            </button>
        </div>
    );
}
