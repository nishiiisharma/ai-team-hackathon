import React, { useState } from 'react';
import { Bot, User, BrainCircuit } from 'lucide-react';
import MenuUpload from './components/MenuUpload';
import AnalyzeMenu from './components/AnalyzeMenu';
import IngredientTable from './components/IngredientTable';
import PredictionTable from './components/PredictionTable';
import CartTable from './components/CartTable';

export default function App() {
    const [userId, setUserId] = useState(1);
    const [step, setStep] = useState(1); // 1 to 5 to handle UI reveal logic

    const handleUploadSuccess = () => setStep(2);
    const handleAnalyzeSuccess = () => setStep(3);
    const handleStockSuccess = () => setStep(4);
    const handlePredictSuccess = () => setStep(5);

    return (
        <div className="min-h-screen p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <header className="mb-12 text-center fade-in">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl shadow-[0_0_40px_rgba(99,102,241,0.6)] mb-6">
                        <Bot size={32} className="text-white" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black mb-4 tracking-tight">
                        Kombee<span className="text-indigo-500">AI</span> Pipeline
                    </h1>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        End-to-End Orchestration: Ingestion, Extraction, PostgreSQL Lookup, and AI Prediction.
                    </p>
                </header>

                <main className="relative">
                    {/* Progress tracking line connecting steps */}
                    <div className="absolute left-6 top-8 bottom-8 w-px bg-white/10 hidden md:block"></div>

                    {/* Global Configuration */}
                    <div className="bg-[#18181b] border border-white/10 rounded-2xl p-6 mb-8 flex items-center justify-between z-10 relative">
                        <div className="flex items-center gap-3">
                            <BrainCircuit className="text-indigo-400" />
                            <span className="font-bold">Session Context</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <label className="text-sm font-semibold text-slate-400">Target User ID:</label>
                            <div className="relative">
                                <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                <input
                                    type="number"
                                    value={userId}
                                    onChange={(e) => {
                                        setUserId(e.target.value);
                                        setStep(1); // Reset workflow if user changes
                                    }}
                                    className="bg-black/50 border border-white/10 pl-9 pr-3 py-2 rounded-lg text-white font-mono w-24 outline-none focus:border-indigo-500 transition-colors"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="relative z-10 pl-0 md:pl-16 space-y-4">
                        <MenuUpload
                            userId={userId}
                            onUploadSuccess={handleUploadSuccess}
                        />

                        <AnalyzeMenu
                            userId={userId}
                            disabled={step < 2}
                            onAnalyzeSuccess={handleAnalyzeSuccess}
                        />

                        <IngredientTable
                            userId={userId}
                            disabled={step < 3}
                            onStockSuccess={handleStockSuccess}
                        />

                        <PredictionTable
                            userId={userId}
                            disabled={step < 4}
                            onPredictSuccess={handlePredictSuccess}
                        />

                        <CartTable
                            userId={userId}
                            disabled={step < 5}
                        />
                    </div>
                </main>
            </div>
        </div>
    );
}
