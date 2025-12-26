/**
 * AI Translation Benchmark - History Panel Component
 * 
 * Author: Zoltan Tamas Toth
 * Date: 2025-12-26
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api, { RunListItem } from '../api/client';

export default function HistoryPanel() {
    const [selectedRun, setSelectedRun] = useState<number | null>(null);
    const [page, setPage] = useState(0);
    const pageSize = 20;

    const { data: runs, isLoading, error } = useQuery({
        queryKey: ['runs', page],
        queryFn: () => api.listRuns(pageSize, page * pageSize),
    });

    const { data: runDetails } = useQuery({
        queryKey: ['run', selectedRun],
        queryFn: () => api.getRun(selectedRun!),
        enabled: selectedRun !== null,
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-12">
                <div className="text-gray-500">Loading history...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card">
                <div className="text-red-600">Failed to load history</div>
            </div>
        );
    }

    if (!runs || runs.length === 0) {
        return (
            <div className="card text-center p-12">
                <div className="text-gray-500 text-lg">No translation runs yet</div>
                <div className="text-gray-400 text-sm mt-2">
                    Run your first translation to see it here
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="card">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-900">Translation History</h2>
                    <button
                        onClick={() => window.location.reload()}
                        className="text-sm text-primary-600 hover:text-primary-700"
                    >
                        Refresh
                    </button>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Date
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Languages
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Text Preview
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Providers
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Avg Score
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {runs.map((run) => (
                                <tr
                                    key={run.id}
                                    onClick={() => setSelectedRun(run.id)}
                                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                                >
                                    <td className="px-4 py-3 text-sm text-gray-900">
                                        {new Date(run.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600">
                                        {run.source_lang || 'auto'} → {run.target_lang}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600 max-w-md truncate">
                                        {run.source_text_preview}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600">
                                        {run.provider_count}
                                    </td>
                                    <td className="px-4 py-3 text-sm font-medium">
                                        {run.avg_score !== null ? (
                                            <span className="text-primary-600">
                                                {run.avg_score.toFixed(1)}
                                            </span>
                                        ) : (
                                            <span className="text-gray-400">-</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="flex justify-between items-center mt-4 pt-4 border-t">
                    <button
                        onClick={() => setPage(Math.max(0, page - 1))}
                        disabled={page === 0}
                        className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Previous
                    </button>
                    <span className="text-sm text-gray-600">
                        Page {page + 1}
                    </span>
                    <button
                        onClick={() => setPage(page + 1)}
                        disabled={runs.length < pageSize}
                        className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Next
                    </button>
                </div>
            </div>

            {selectedRun && runDetails && (
                <div className="card">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-bold text-gray-900">Run Details</h3>
                        <button
                            onClick={() => setSelectedRun(null)}
                            className="text-sm text-gray-500 hover:text-gray-700"
                        >
                            Close
                        </button>
                    </div>
                    <div className="text-sm text-gray-600 mb-4">
                        <strong>Source:</strong> {runDetails.source_text}
                    </div>
                    <div className="space-y-4">
                        {runDetails.results.map((result, idx) => (
                            <div key={idx} className="border rounded-lg p-4">
                                <div className="font-medium text-gray-900 mb-2">
                                    {result.translation.provider_name} - {result.translation.model_id}
                                </div>
                                <div className="text-gray-700 mb-2">
                                    {result.translation.output_text}
                                </div>
                                <div className="flex gap-4 text-xs text-gray-500">
                                    <span>Score: {result.evaluation.score_breakdown.overall_score.toFixed(1)}</span>
                                    <span>Latency: {result.translation.latency_ms.toFixed(0)}ms</span>
                                    {result.translation.usage_tokens && (
                                        <span>Tokens: {result.translation.usage_tokens}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
