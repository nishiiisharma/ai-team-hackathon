import React, { useState } from 'react';
import { analyzeMenu } from '../services/api';
import { BrainCircuit, Loader2, AlertCircle, FileText } from 'lucide-react';

export default function AnalyzeMenu({ userId, onAnalyzeSuccess, disabled }) {
    const [status, setStatus] = useState('idle');
    const [data, setData] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    const handleAnalyze = async () => {
        setStatus('analyzing');
        try {
            const res = await analyzeMenu(userId);
            setData(res);
            setStatus('success');
            onAnalyzeSuccess(res);
        } catch (err) {
            setStatus('error');
            setErrorMsg(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div className={`bg-[#18181b] border border-white/10 rounded-2xl p-8 mb-8 shadow-xl transition-opacity ${disabled ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-purple-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span>
                Analyze Menu Structure
            </h2>
            <p className="text-slate-400 mb-6 text-sm">Extract dishes and identify their constituent ingredients using LLMs.</p>

            <button
                onClick={handleAnalyze}
                disabled={status === 'analyzing' || status === 'success'}
                className="w-full py-4 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl font-bold transition-all flex justify-center items-center gap-2 shadow-lg shadow-purple-900/20"
            >
                {status === 'analyzing' ? <Loader2 className="animate-spin" size={20} /> : <BrainCircuit size={20} />}
                {status === 'analyzing' ? 'Intelligent Extraction...' : 'Analyze Menu'}
            </button>

            {status === 'error' && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-center gap-2 text-sm">
                    <AlertCircle size={16} /> {errorMsg}
                </div>
            )}

            {status === 'success' && data && (
                <div className="mt-8 bg-black/40 border border-white/5 rounded-xl p-6 fade-in">
                    <h3 className="text-slate-300 font-semibold mb-4 flex items-center gap-2">
                        <FileText size={16} className="text-emerald-400" />
                        Dishes Identified ({data.dishes.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {data.dishes.map((dish, i) => (
                            <div key={i} className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-slate-300">
                                {dish.name}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
