/**
 * AI Translation Benchmark - Statistics Summary Component
 * 
 * Author: Zoltan Tamas Toth
 * Date: 2025-12-25
 * 
 * Displays comparative statistics across all translation results.
 */

import { TranslationWithEvaluation } from '../api/client';

interface StatisticsSummaryProps {
    results: TranslationWithEvaluation[];
}

export default function StatisticsSummary({ results }: StatisticsSummaryProps) {
    if (results.length === 0) {
        return null;
    }

    // Calculate average latency
    const avgLatency = results.reduce((sum, r) => sum + r.translation.latency_ms, 0) / results.length;

    // Calculate score statistics
    const scores = results.map(r => r.evaluation.score_breakdown.overall_score);
    const minScore = Math.min(...scores);
    const maxScore = Math.max(...scores);
    const avgScore = scores.reduce((sum, s) => sum + s, 0) / scores.length;

    // Calculate standard deviation
    const variance = scores.reduce((sum, s) => sum + Math.pow(s - avgScore, 2), 0) / scores.length;
    const stdDev = Math.sqrt(variance);

    // Get all unique metric names
    const metricNames = new Set<string>();
    results.forEach(r => {
        r.evaluation.score_breakdown.metrics.forEach(m => {
            metricNames.add(m.name);
        });
    });

    // Calculate best/worst for each metric
    const metricStats = Array.from(metricNames).map(metricName => {
        const values = results
            .map(r => {
                const metric = r.evaluation.score_breakdown.metrics.find(m => m.name === metricName);
                return metric ? metric.value : null;
            })
            .filter((v): v is number => v !== null);

        if (values.length === 0) {
            return null;
        }

        return {
            name: metricName,
            min: Math.min(...values),
            max: Math.max(...values),
            avg: values.reduce((sum, v) => sum + v, 0) / values.length,
        };
    }).filter((s): s is NonNullable<typeof s> => s !== null);

    return (
        <div className="card">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Comparative Statistics</h3>

            {/* Overall Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4">
                    <div className="text-sm text-blue-600 font-medium mb-1">Avg Latency</div>
                    <div className="text-2xl font-bold text-blue-900">{avgLatency.toFixed(0)}ms</div>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                    <div className="text-sm text-green-600 font-medium mb-1">Best Score</div>
                    <div className="text-2xl font-bold text-green-900">{maxScore.toFixed(1)}</div>
                </div>

                <div className="bg-orange-50 rounded-lg p-4">
                    <div className="text-sm text-orange-600 font-medium mb-1">Worst Score</div>
                    <div className="text-2xl font-bold text-orange-900">{minScore.toFixed(1)}</div>
                </div>

                <div className="bg-purple-50 rounded-lg p-4">
                    <div className="text-sm text-purple-600 font-medium mb-1">Score Variance</div>
                    <div className="text-2xl font-bold text-purple-900">±{stdDev.toFixed(1)}</div>
                </div>
            </div>

            {/* Metric-by-Metric Comparison */}
            {metricStats.length > 0 && (
                <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">Metric Comparison</h4>
                    <div className="space-y-2">
                        {metricStats.map((stat) => (
                            <div key={stat.name} className="bg-gray-50 rounded p-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-gray-700 capitalize">
                                        {stat.name.replace(/_/g, ' ')}
                                    </span>
                                    <div className="flex gap-4 text-xs text-gray-600">
                                        <span>Min: <strong>{stat.min.toFixed(1)}</strong></span>
                                        <span>Avg: <strong>{stat.avg.toFixed(1)}</strong></span>
                                        <span>Max: <strong>{stat.max.toFixed(1)}</strong></span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Additional Info */}
            <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                    <p>
                        <strong>Score Variance (±{stdDev.toFixed(1)}):</strong>{' '}
                        {stdDev < 5
                            ? 'Very consistent results across providers'
                            : stdDev < 10
                                ? 'Moderate variation between providers'
                                : 'Significant differences in provider performance'}
                    </p>
                </div>
            </div>
        </div>
    );
}
