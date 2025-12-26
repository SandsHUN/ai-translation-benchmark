/**
 * AI Translation Benchmark - Model Card Component
 * 
 * Author: Zoltan Tamas Toth
 */

import { useState } from 'react';
import { TranslationWithEvaluation } from '../api/client';
import ScoreBreakdown from './ScoreBreakdown';

interface ModelCardProps {
    result: TranslationWithEvaluation;
    rank: number;
}

export default function ModelCard({ result, rank }: ModelCardProps) {
    const [activeTab, setActiveTab] = useState<'output' | 'scores' | 'diagnostics'>('output');
    const { translation, evaluation } = result;

    const getScoreClass = (score: number) => {
        if (score >= 90) return 'score-excellent';
        if (score >= 75) return 'score-good';
        if (score >= 60) return 'score-fair';
        return 'score-poor';
    };

    const getRankBadge = () => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    };

    return (
        <div className="card">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-lg font-bold text-gray-900">
                        {translation.provider_name}
                    </h3>
                    <p className="text-sm text-gray-500">{translation.model_id}</p>
                </div>
                <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getRankBadge()}</span>
                    <div className={`metric-badge ${getScoreClass(evaluation.score_breakdown.overall_score)}`}>
                        {evaluation.score_breakdown.overall_score.toFixed(1)}
                    </div>
                </div>
            </div>

            {/* Metadata */}
            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                <span>⚡ {translation.latency_ms.toFixed(0)}ms</span>
                {translation.usage_tokens && (
                    <span>🎫 {translation.usage_tokens} tokens</span>
                )}
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200 mb-4">
                <nav className="flex space-x-4">
                    {(['output', 'scores', 'diagnostics'] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab
                                    ? 'border-primary-600 text-primary-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Tab Content */}
            <div className="min-h-[200px]">
                {activeTab === 'output' && (
                    <div>
                        {translation.error ? (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-red-800 font-medium">Translation Failed</p>
                                <p className="text-red-600 text-sm mt-1">{translation.error}</p>
                            </div>
                        ) : (
                            <div className="bg-gray-50 rounded-lg p-4">
                                <p className="text-gray-900 whitespace-pre-wrap">{translation.output_text}</p>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'scores' && (
                    <ScoreBreakdown scoreBreakdown={evaluation.score_breakdown} />
                )}

                {activeTab === 'diagnostics' && (
                    <div className="space-y-3">
                        {evaluation.score_breakdown.explanation && (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                <p className="text-blue-900 text-sm">{evaluation.score_breakdown.explanation}</p>
                            </div>
                        )}

                        {evaluation.score_breakdown.warnings.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-900">Warnings</h4>
                                {evaluation.score_breakdown.warnings.map((warning, idx) => (
                                    <div key={idx} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                                        <p className="text-yellow-800 text-sm">{warning}</p>
                                    </div>
                                ))}
                            </div>
                        )}

                        {evaluation.score_breakdown.warnings.length === 0 && !translation.error && (
                            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                <p className="text-green-800 text-sm">✓ No issues detected</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
