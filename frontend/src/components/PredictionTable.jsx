import React, { useState } from 'react';
import { predictQuantity } from '../services/api';
import { TrendingUp, Loader2, AlertCircle } from 'lucide-react';

export default function PredictionTable({ userId, onPredictSuccess, disabled }) {
    const [status, setStatus] = useState('idle');
    const [data, setData] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    const handlePredict = async () => {
        setStatus('predicting');
        try {
            const res = await predictQuantity(userId);
            setData(res);
            setStatus('success');
            onPredictSuccess();
        } catch (err) {
            setStatus('error');
            setErrorMsg(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div className={`bg-[#18181b] border border-white/10 rounded-2xl p-8 mb-8 shadow-xl transition-opacity ${disabled ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-emerald-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">4</span>
                Ingredient Prediction Module
            </h2>
            <p className="text-slate-400 mb-6 text-sm">Forecast the quantity required for the next 7 days based on 20,000 historical order points.</p>

            <button
                onClick={handlePredict}
                disabled={status === 'predicting' || status === 'success'}
                className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl font-bold transition-all flex justify-center items-center gap-2"
            >
                {status === 'predicting' ? <Loader2 className="animate-spin" size={20} /> : <TrendingUp size={20} />}
                {status === 'predicting' ? 'Running Model Parameters...' : 'Predict Required Quantity'}
            </button>

            {status === 'error' && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-center gap-2 text-sm">
                    <AlertCircle size={16} /> {errorMsg}
                </div>
            )}

            {status === 'success' && data && (
                <div className="mt-8 rounded-xl overflow-hidden border border-white/5 fade-in">
                    <table className="w-full text-left bg-black/40">
                        <thead>
                            <tr className="bg-white/5 border-b border-white/5 text-xs text-slate-500 uppercase">
                                <th className="px-6 py-4 font-semibold">Ingredient</th>
                                <th className="px-6 py-4 font-semibold">Predicted Required (KG)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {data.predictions.map((item, i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 text-emerald-200 capitalize font-medium">{item.ingredient}</td>
                                    <td className="px-6 py-4 text-slate-400 font-mono">{item.predicted_quantity.toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
