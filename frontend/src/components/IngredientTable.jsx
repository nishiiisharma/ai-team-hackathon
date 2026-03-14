import React, { useState } from 'react';
import { getIngredientsStock } from '../services/api';
import { Database, Loader2, AlertCircle } from 'lucide-react';

export default function IngredientTable({ userId, onStockSuccess, disabled }) {
    const [status, setStatus] = useState('idle');
    const [data, setData] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    const handleGetStock = async () => {
        setStatus('fetching');
        try {
            const res = await getIngredientsStock(userId);
            setData(res);
            setStatus('success');
            onStockSuccess();
        } catch (err) {
            setStatus('error');
            setErrorMsg(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div className={`bg-[#18181b] border border-white/10 rounded-2xl p-8 mb-8 shadow-xl transition-opacity ${disabled ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-sky-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">3</span>
                Ingredient Stock Query
            </h2>
            <p className="text-slate-400 mb-6 text-sm">Query the PostgreSQL database for the extracted ingredients' availability.</p>

            <button
                onClick={handleGetStock}
                disabled={status === 'fetching' || status === 'success'}
                className="w-full py-4 bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl font-bold transition-all flex justify-center items-center gap-2"
            >
                {status === 'fetching' ? <Loader2 className="animate-spin" size={20} /> : <Database size={20} />}
                {status === 'fetching' ? 'Connecting to Database...' : 'Check Current Stock'}
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
                                <th className="px-6 py-4 font-semibold">Current Stock (KG)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {data.stock.map((item, i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 text-sky-200 capitalize font-medium">{item.ingredient}</td>
                                    <td className="px-6 py-4 text-slate-400 font-mono">{item.available_stock.toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
