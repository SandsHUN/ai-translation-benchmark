/**
 * AI Translation Benchmark - Ranking Summary Component
 * 
 * Author: Zoltan Tamas Toth
 */

import { RunSummary } from '../api/client';

interface RankingSummaryProps {
    summary: RunSummary;
}

export default function RankingSummary({ summary }: RankingSummaryProps) {
    return (
        <div className="card bg-gradient-to-br from-primary-50 to-primary-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Summary</h2>

            {summary.best_provider && (
                <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-1">Best Provider</p>
                    <div className="flex items-center justify-between">
                        <p className="text-lg font-bold text-primary-700">{summary.best_provider}</p>
                        <span className="text-2xl font-bold text-primary-600">
                            {summary.best_score?.toFixed(1)}
                        </span>
                    </div>
                </div>
            )}

            <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Rankings</p>
                <div className="space-y-2">
                    {summary.rankings.map((ranking) => (
                        <div
                            key={ranking.rank}
                            className="flex items-center justify-between bg-white rounded-lg p-3 shadow-sm"
                        >
                            <div className="flex items-center space-x-3">
                                <span className="text-lg font-bold text-gray-400 w-6">
                                    {ranking.rank === 1 ? '🥇' : ranking.rank === 2 ? '🥈' : ranking.rank === 3 ? '🥉' : `#${ranking.rank}`}
                                </span>
                                <div>
                                    <p className="font-medium text-gray-900">{ranking.provider}</p>
                                    <p className="text-xs text-gray-500">{ranking.latency_ms.toFixed(0)}ms</p>
                                </div>
                            </div>
                            <span className="font-bold text-gray-700">{ranking.score.toFixed(1)}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
