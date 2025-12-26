import { useState } from 'react';
import InputPanel from './components/InputPanel';
import OutputPanel from './components/OutputPanel';
import HistoryPanel from './components/HistoryPanel';
import { TranslationResponse } from './api/client';

function App() {
    const [results, setResults] = useState<TranslationResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'new' | 'history'>('new');

    const handleTranslationComplete = (response: TranslationResponse) => {
        setResults(response);
        setIsLoading(false);
    };

    const handleTranslationStart = () => {
        setIsLoading(true);
        setResults(null);
    };

    return (
        <div className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                <header className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">
                        AI Translation Benchmark
                    </h1>
                    <p className="text-lg text-gray-600">
                        Compare translation quality across multiple providers
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                        Evaluated using BLEU, chrF, BERTScore and semantic similarity metrics
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                        by Zoltan Tamas Toth
                    </p>
                </header>

                <div className="mb-8 flex justify-center gap-4">
                    <button
                        onClick={() => setActiveTab('new')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${activeTab === 'new'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                    >
                        New Translation
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${activeTab === 'history'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                    >
                        History
                    </button>
                </div>

                {activeTab === 'new' ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div>
                            <InputPanel
                                onTranslationStart={handleTranslationStart}
                                onTranslationComplete={handleTranslationComplete}
                                isLoading={isLoading}
                            />
                        </div>
                        <div>
                            <OutputPanel results={results} isLoading={isLoading} />
                        </div>
                    </div>
                ) : (
                    <HistoryPanel />
                )}

                <footer className="mt-16 text-center text-sm text-gray-500">
                    <p>
                        AI Translation Benchmark v0.1.0 | Open Source Project
                    </p>
                </footer>
            </div>
        </div>
    );
}

export default App;
