/**
 * AI Translation Benchmark - Output Panel Component
 * 
 * Author: Zoltan Tamas Toth
 * Date: 2025-12-25
 */

import { TranslationResponse } from '../api/client';
import ModelCard from './ModelCard';
import RankingSummary from './RankingSummary';
import StatisticsSummary from './StatisticsSummary';

interface OutputPanelProps {
    results: TranslationResponse | null;
    isLoading: boolean;
}

export default function OutputPanel({ results, isLoading }: OutputPanelProps) {
    if (isLoading) {
        return (
            <div className="card">
                <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                        <svg className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <p className="text-gray-600 font-medium">Processing translations...</p>
                        <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!results) {
        return (
            <div className="card">
                <div className="text-center py-12">
                    <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-gray-500">No results yet</p>
                    <p className="text-sm text-gray-400 mt-2">Enter text and select providers to begin</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Ranking Summary */}
            <RankingSummary summary={results.summary} />

            {/* Statistics Summary */}
            <StatisticsSummary results={results.results} />

            {/* Model Cards */}
            <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-900">Translation Results</h2>
                {results.results.map((result, index) => (
                    <ModelCard
                        key={index}
                        result={result}
                        rank={results.summary.rankings.find(
                            (r) => r.provider === result.translation.provider_name
                        )?.rank || 0}
                    />
                ))}
            </div>
        </div>
    );
}
