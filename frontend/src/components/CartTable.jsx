import React, { useState } from 'react';
import { getCart } from '../services/api';
import { ShoppingCart, Loader2, AlertCircle } from 'lucide-react';

export default function CartTable({ userId, disabled }) {
    const [status, setStatus] = useState('idle');
    const [data, setData] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    const handleCart = async () => {
        setStatus('fetching');
        try {
            const res = await getCart(userId);
            setData(res);
            setStatus('success');
        } catch (err) {
            setStatus('error');
            setErrorMsg(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div className={`bg-[#18181b] border border-white/10 rounded-2xl p-8 mb-8 shadow-xl transition-opacity ${disabled ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="bg-orange-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">5</span>
                Final Cart Recommendation
            </h2>
            <p className="text-slate-400 mb-6 text-sm">Synthesize data to generate the final optimized purchase cart.</p>

            <button
                onClick={handleCart}
                disabled={status === 'fetching' || status === 'success'}
                className="w-full py-4 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl font-bold transition-all flex justify-center items-center gap-2"
            >
                {status === 'fetching' ? <Loader2 className="animate-spin" size={20} /> : <ShoppingCart size={20} />}
                {status === 'fetching' ? 'Optimizing Cart...' : 'Generate Purchase Cart'}
            </button>

            {status === 'error' && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-center gap-2 text-sm">
                    <AlertCircle size={16} /> {errorMsg}
                </div>
            )}

            {status === 'success' && data && (
                <div className="mt-8 rounded-xl overflow-hidden border border-white/5 shadow-2xl fade-in">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left bg-black/40 min-w-max">
                            <thead>
                                <tr className="bg-orange-950/20 border-b border-orange-500/20 text-xs text-orange-200/50 uppercase tracking-widest font-black">
                                    <th className="px-6 py-4">Ingredient</th>
                                    <th className="px-6 py-4">Available Stock</th>
                                    <th className="px-6 py-4">Predicted Needed</th>
                                    <th className="px-6 py-4">Recommended Order</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {data.cart.length > 0 ? data.cart.map((item, i) => (
                                    <tr key={i} className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-5 text-indigo-200 font-bold capitalize">{item.ingredient}</td>
                                        <td className="px-6 py-5 text-slate-400 font-mono">{item.available_stock.toFixed(2)} kg</td>
                                        <td className="px-6 py-5 text-emerald-400 font-mono">{item.predicted_required_quantity.toFixed(2)} kg</td>
                                        <td className="px-6 py-5">
                                            <span className="bg-orange-600 text-white font-black px-4 py-2 rounded-xl text-xs tracking-wider shadow-[0_0_15px_rgba(234,88,12,0.5)]">
                                                {item.recommended_order_quantity.toFixed(2)} KG
                                            </span>
                                        </td>
                                    </tr>
                                )) : (
                                    <tr>
                                        <td colSpan="4" className="px-6 py-12 text-center text-slate-500 italic">No restocking required. Inventory is sufficient.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
