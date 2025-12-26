/**
 * AI Translation Benchmark - Score Breakdown Component
 * 
 * Author: Zoltan Tamas Toth
 */

import { ScoreBreakdown as ScoreBreakdownType } from '../api/client';

interface ScoreBreakdownProps {
    scoreBreakdown: ScoreBreakdownType;
}

export default function ScoreBreakdown({ scoreBreakdown }: ScoreBreakdownProps) {
    const getScoreColor = (score: number) => {
        if (score >= 90) return 'bg-green-500';
        if (score >= 75) return 'bg-blue-500';
        if (score >= 60) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    const formatMetricName = (name: string) => {
        return name
            .split('_')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    return (
        <div className="space-y-4">
            {/* Overall Score */}
            <div className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg p-4">
                <div className="flex items-center justify-between">
                    <span className="text-lg font-medium text-gray-900">Overall Score</span>
                    <span className="text-2xl font-bold text-primary-700">
                        {scoreBreakdown.overall_score.toFixed(1)}
                    </span>
                </div>
            </div>

            {/* Individual Metrics */}
            <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Metric Breakdown</h4>
                {scoreBreakdown.metrics.map((metric, idx) => (
                    <div key={idx} className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-700">{formatMetricName(metric.name)}</span>
                            <span className="font-medium text-gray-900">
                                {metric.value.toFixed(1)}
                                <span className="text-gray-500 text-xs ml-1">
                                    (weight: {(metric.weight * 100).toFixed(0)}%)
                                </span>
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className={`h-2 rounded-full transition-all duration-300 ${getScoreColor(metric.value)}`}
                                style={{ width: `${metric.value}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
