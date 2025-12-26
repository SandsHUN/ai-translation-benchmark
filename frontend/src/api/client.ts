/**
 * AI Translation Benchmark - API Client
 * 
 * Author: Zoltan Tamas Toth
 * Date: 2025-12-25
 * 
 * HTTP client for backend API communication.
 */

import axios from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 300000, // 5 minutes for slow local models
});

export interface ProviderRequest {
    type: string;
    model: string;
    base_url?: string;
    api_key?: string;
}

export interface TranslationRequest {
    text: string;
    target_lang: string;
    source_lang?: string;
    providers: ProviderRequest[];
    reference_translation?: string;
    timeout?: number;
}

export interface TranslationResult {
    provider_name: string;
    model_id: string;
    output_text: string;
    latency_ms: number;
    usage_tokens?: number;
    error?: string;
}

export interface MetricResult {
    name: string;
    value: number;
    weight: number;
    details?: any;
}

export interface ScoreBreakdown {
    overall_score: number;
    metrics: MetricResult[];
    warnings: string[];
    explanation?: string;
}

export interface EvaluationResult {
    translation_id: number;
    provider_name: string;
    model_id: string;
    score_breakdown: ScoreBreakdown;
}

export interface TranslationWithEvaluation {
    translation: TranslationResult;
    evaluation: EvaluationResult;
}

export interface RunSummary {
    total_providers: number;
    rankings: Array<{
        rank: number;
        provider: string;
        model: string;
        score: number;
        latency_ms: number;
    }>;
    best_provider?: string;
    best_score?: number;
}

export interface TranslationResponse {
    run_id: number;
    source_text: string;
    target_lang: string;
    source_lang?: string;
    results: TranslationWithEvaluation[];
    summary: RunSummary;
    created_at: string;
}

export interface RunListItem {
    id: number;
    created_at: string;
    source_lang: string | null;
    target_lang: string;
    source_text_preview: string;
    provider_count: number;
    avg_score: number | null;
}

export interface ProviderInfo {
    type: string;
    name: string;
    model: string;
    enabled: boolean;
}

export const api = {
    async runTranslation(request: TranslationRequest): Promise<TranslationResponse> {
        const response = await apiClient.post<TranslationResponse>('/run', request);
        return response.data;
    },

    async getRun(runId: number): Promise<TranslationResponse> {
        const response = await apiClient.get<TranslationResponse>(`/run/${runId}`);
        return response.data;
    },

    async getProviders(): Promise<ProviderInfo[]> {
        const response = await apiClient.get<ProviderInfo[]>('/providers');
        return response.data;
    },

    async healthCheck(): Promise<{ status: string; version: string }> {
        const response = await apiClient.get('/health');
        return response.data;
    },

    async listRuns(limit = 50, offset = 0): Promise<RunListItem[]> {
        const response = await apiClient.get<RunListItem[]>('/runs', {
            params: { limit, offset },
        });
        return response.data;
    },
};

export default api;
