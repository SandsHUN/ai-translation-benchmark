/**
 * AI Translation Benchmark - Input Panel Component
 * 
 * Author: Zoltan Tamas Toth
 * Date: 2025-12-25
 */

import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import api, { ProviderRequest, TranslationRequest, TranslationResponse } from '../api/client';

interface InputPanelProps {
    onTranslationStart: () => void;
    onTranslationComplete: (response: TranslationResponse) => void;
    isLoading: boolean;
}

const LANGUAGES = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'ru', name: 'Russian' },
    { code: 'ar', name: 'Arabic' },
    { code: 'hi', name: 'Hindi' },
    { code: 'hu', name: 'Hungarian' },
    { code: 'vi', name: 'Vietnamese' },
    { code: 'th', name: 'Thai' },
];

const MAX_TEXT_LENGTH = 5000;

export default function InputPanel({ onTranslationStart, onTranslationComplete, isLoading }: InputPanelProps) {
    const [text, setText] = useState('The future of artificial intelligence is not about replacing humans, but augmenting our capabilities.');
    const [sourceLang, setSourceLang] = useState('');
    const [targetLang, setTargetLang] = useState('es');

    // Provider configurations
    const [useOpenAI, setUseOpenAI] = useState(false);
    const [openAIKey, setOpenAIKey] = useState('');
    const [openAIModel, setOpenAIModel] = useState('gpt-4');

    const [useLMStudio, setUseLMStudio] = useState(false);
    const [lmStudioUrl, setLMStudioUrl] = useState('http://192.168.1.68:1234/v1');
    const [lmStudioModel, setLMStudioModel] = useState('');
    const [lmStudioModels, setLMStudioModels] = useState<string[]>([]);
    const [loadingModels, setLoadingModels] = useState(false);

    const [useDeepL, setUseDeepL] = useState(false);
    const [deeplKey, setDeepLKey] = useState('');

    const [useGoogle, setUseGoogle] = useState(false);
    const [googleKey, setGoogleKey] = useState('');

    const [useOllama, setUseOllama] = useState(false);
    const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434/v1');
    const [ollamaModel, setOllamaModel] = useState('llama2');
    const [ollamaModels, setOllamaModels] = useState<string[]>([]);
    const [loadingOllamaModels, setLoadingOllamaModels] = useState(false);

    // Fetch available models from LM Studio when URL changes
    useEffect(() => {
        const fetchModels = async () => {
            if (!lmStudioUrl || !lmStudioUrl.trim()) {
                setLMStudioModels([]);
                return;
            }

            setLoadingModels(true);
            try {
                // Remove /v1 suffix if present and add /v1/models
                const baseUrl = lmStudioUrl.replace(/\/v1\/?$/, '');
                const modelsUrl = `${baseUrl}/v1/models`;

                const response = await fetch(modelsUrl);
                if (response.ok) {
                    const data = await response.json();
                    if (data.data && Array.isArray(data.data)) {
                        const modelIds = data.data.map((model: { id: string }) => model.id);
                        setLMStudioModels(modelIds);
                        // Set first model as default if available
                        if (modelIds.length > 0 && !lmStudioModel) {
                            setLMStudioModel(modelIds[0]);
                        }
                    }
                }
            } catch (error) {
                console.error('Failed to fetch LM Studio models:', error);
                setLMStudioModels([]);
            } finally {
                setLoadingModels(false);
            }
        };

        // Debounce the fetch to avoid too many requests while typing
        const timeoutId = setTimeout(fetchModels, 500);
        return () => clearTimeout(timeoutId);
    }, [lmStudioUrl, lmStudioModel, useLMStudio]);

    // Fetch available models from Ollama when URL changes
    useEffect(() => {
        const fetchModels = async () => {
            if (!ollamaUrl || !ollamaUrl.trim()) {
                setOllamaModels([]);
                return;
            }

            setLoadingOllamaModels(true);
            try {
                // Remove /v1 suffix if present and add /v1/models
                const baseUrl = ollamaUrl.replace(/\/v1\/?$/, '');
                const modelsUrl = `${baseUrl}/v1/models`;

                const response = await fetch(modelsUrl);
                if (response.ok) {
                    const data = await response.json();
                    if (data.data && Array.isArray(data.data)) {
                        const modelIds = data.data.map((model: { id: string }) => model.id);
                        setOllamaModels(modelIds);
                        // Set first model as default if available
                        if (modelIds.length > 0 && !ollamaModel) {
                            setOllamaModel(modelIds[0]);
                        }
                    }
                }
            } catch (error) {
                console.error('Failed to fetch Ollama models:', error);
                setOllamaModels([]);
            } finally {
                setLoadingOllamaModels(false);
            }
        };

        // Debounce the fetch to avoid too many requests while typing
        const timeoutId = setTimeout(fetchModels, 500);
        return () => clearTimeout(timeoutId);
    }, [ollamaUrl, ollamaModel, useOllama]);

    const mutation = useMutation({
        mutationFn: (request: TranslationRequest) => api.runTranslation(request),
        onSuccess: (data) => {
            onTranslationComplete(data);
        },
        onError: (error: { response?: { data?: { detail?: string } }; message: string }) => {
            alert(`Translation failed: ${error.response?.data?.detail || error.message}`);
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Validation
        if (!text.trim()) {
            alert('Please enter text to translate');
            return;
        }

        if (text.length > MAX_TEXT_LENGTH) {
            alert(`Text is too long. Maximum ${MAX_TEXT_LENGTH} characters allowed.`);
            return;
        }

        if (!useOpenAI && !useLMStudio && !useDeepL && !useGoogle && !useOllama) {
            alert('Please select at least one provider');
            return;
        }

        if (useOpenAI && !openAIKey.trim()) {
            alert('Please enter your OpenAI API key');
            return;
        }

        if (useLMStudio && !lmStudioUrl.trim()) {
            alert('Please enter LM Studio endpoint URL');
            return;
        }

        if (useDeepL && !deeplKey.trim()) {
            alert('Please enter DeepL API key');
            return;
        }

        if (useGoogle && !googleKey.trim()) {
            alert('Please enter Google Cloud API key');
            return;
        }

        if (useOllama && !ollamaUrl.trim()) {
            alert('Please enter Ollama endpoint URL');
            return;
        }

        // Build provider requests
        const providerRequests: ProviderRequest[] = [];

        if (useOpenAI) {
            providerRequests.push({
                type: 'openai',
                model: openAIModel,
                api_key: openAIKey,
            });
        }

        if (useLMStudio) {
            providerRequests.push({
                type: 'local_openai',
                model: lmStudioModel,
                base_url: lmStudioUrl,
            });
        }

        if (useDeepL) {
            providerRequests.push({
                type: 'deepl',
                model: 'deepl',
                api_key: deeplKey,
            });
        }

        if (useGoogle) {
            providerRequests.push({
                type: 'google_translate',
                model: 'default',
                api_key: googleKey,
            });
        }

        if (useOllama) {
            providerRequests.push({
                type: 'local_openai',
                model: ollamaModel,
                base_url: ollamaUrl,
            });
        }

        const request: TranslationRequest = {
            text,
            target_lang: targetLang,
            source_lang: sourceLang || undefined,
            providers: providerRequests,
        };

        onTranslationStart();
        mutation.mutate(request);
    };

    const charCount = text.length;
    const isOverLimit = charCount > MAX_TEXT_LENGTH;

    return (
        <div className="card">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Translation Input</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Text Input */}
                <div>
                    <label htmlFor="text" className="label">
                        Text to Translate *
                    </label>
                    <textarea
                        id="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        className={`textarea-field ${isOverLimit ? 'border-red-500' : ''}`}
                        rows={6}
                        placeholder="Enter text to translate..."
                        disabled={isLoading}
                    />
                    <div className={`text-sm mt-1 ${isOverLimit ? 'text-red-600' : 'text-gray-500'}`}>
                        {charCount} / {MAX_TEXT_LENGTH} characters
                    </div>
                </div>

                {/* Language Selection */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="sourceLang" className="label">
                            Source Language (Optional)
                        </label>
                        <select
                            id="sourceLang"
                            value={sourceLang}
                            onChange={(e) => setSourceLang(e.target.value)}
                            className="select-field"
                            disabled={isLoading}
                        >
                            <option value="">Auto-detect</option>
                            {LANGUAGES.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label htmlFor="targetLang" className="label">
                            Target Language *
                        </label>
                        <select
                            id="targetLang"
                            value={targetLang}
                            onChange={(e) => setTargetLang(e.target.value)}
                            className="select-field"
                            disabled={isLoading}
                            required
                        >
                            {LANGUAGES.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Provider Configuration */}
                <div className="border border-gray-200 rounded-lg p-4 space-y-4">
                    <h3 className="font-medium text-gray-900">Select Providers *</h3>

                    {/* OpenAI Provider */}
                    <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={useOpenAI}
                                onChange={(e) => setUseOpenAI(e.target.checked)}
                                disabled={isLoading}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                            <span className="font-medium text-gray-700">OpenAI</span>
                        </label>

                        {useOpenAI && (
                            <div className="ml-7 space-y-3 bg-gray-50 p-3 rounded">
                                <div>
                                    <label htmlFor="openAIKey" className="label text-sm">
                                        API Key *
                                    </label>
                                    <input
                                        id="openAIKey"
                                        type="password"
                                        value={openAIKey}
                                        onChange={(e) => setOpenAIKey(e.target.value)}
                                        className="input-field text-sm"
                                        placeholder="sk-..."
                                        disabled={isLoading}
                                    />
                                </div>
                                <div>
                                    <label htmlFor="openAIModel" className="label text-sm">
                                        Model
                                    </label>
                                    <select
                                        id="openAIModel"
                                        value={openAIModel}
                                        onChange={(e) => setOpenAIModel(e.target.value)}
                                        className="select-field text-sm"
                                        disabled={isLoading}
                                    >
                                        <option value="gpt-4">GPT-4</option>
                                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    </select>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* LM Studio Provider */}
                    <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={useLMStudio}
                                onChange={(e) => setUseLMStudio(e.target.checked)}
                                disabled={isLoading}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                            <span className="font-medium text-gray-700">LM Studio (Local)</span>
                        </label>

                        {useLMStudio && (
                            <div className="ml-7 space-y-3 bg-gray-50 p-3 rounded">
                                <div>
                                    <label htmlFor="lmStudioUrl" className="label text-sm">
                                        Endpoint URL *
                                    </label>
                                    <input
                                        id="lmStudioUrl"
                                        type="text"
                                        value={lmStudioUrl}
                                        onChange={(e) => setLMStudioUrl(e.target.value)}
                                        className="input-field text-sm"
                                        placeholder="http://192.168.1.68:1234/v1"
                                        disabled={isLoading}
                                    />
                                </div>
                                <div>
                                    <label htmlFor="lmStudioModel" className="label text-sm">
                                        Model {loadingModels && '(Loading...)'}
                                    </label>
                                    {lmStudioModels.length > 0 ? (
                                        <select
                                            id="lmStudioModel"
                                            value={lmStudioModel}
                                            onChange={(e) => setLMStudioModel(e.target.value)}
                                            className="select-field text-sm"
                                            disabled={isLoading || loadingModels}
                                        >
                                            {lmStudioModels.map((model) => (
                                                <option key={model} value={model}>
                                                    {model}
                                                </option>
                                            ))}
                                        </select>
                                    ) : (
                                        <input
                                            id="lmStudioModel"
                                            type="text"
                                            value={lmStudioModel}
                                            onChange={(e) => setLMStudioModel(e.target.value)}
                                            className="input-field text-sm"
                                            placeholder="auto-detect"
                                            disabled={isLoading}
                                        />
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* DeepL Provider */}
                    <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={useDeepL}
                                onChange={(e) => setUseDeepL(e.target.checked)}
                                disabled={isLoading}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                            <span className="font-medium text-gray-700">DeepL (500k chars/month free)</span>
                        </label>

                        {useDeepL && (
                            <div className="ml-7 space-y-3 bg-gray-50 p-3 rounded">
                                <div>
                                    <label htmlFor="deeplKey" className="label text-sm">
                                        API Key *
                                    </label>
                                    <input
                                        id="deeplKey"
                                        type="password"
                                        value={deeplKey}
                                        onChange={(e) => setDeepLKey(e.target.value)}
                                        className="input-field text-sm"
                                        placeholder="Enter DeepL API key"
                                        disabled={isLoading}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Get your free API key at{' '}
                                        <a href="https://www.deepl.com/pro-api" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                                            deepl.com/pro-api
                                        </a>
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Google Translate Provider */}
                    <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={useGoogle}
                                onChange={(e) => setUseGoogle(e.target.checked)}
                                disabled={isLoading}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                            <span className="font-medium text-gray-700">Google Cloud Translation (500k chars/month free)</span>
                        </label>

                        {useGoogle && (
                            <div className="ml-7 space-y-3 bg-gray-50 p-3 rounded">
                                <div>
                                    <label htmlFor="googleKey" className="label text-sm">
                                        API Key *
                                    </label>
                                    <input
                                        id="googleKey"
                                        type="password"
                                        value={googleKey}
                                        onChange={(e) => setGoogleKey(e.target.value)}
                                        className="input-field text-sm"
                                        placeholder="Enter Google Cloud API key"
                                        disabled={isLoading}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Get your API key at{' '}
                                        <a href="https://cloud.google.com/translate" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                                            Google Cloud Console
                                        </a>
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Ollama Provider */}
                    <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={useOllama}
                                onChange={(e) => setUseOllama(e.target.checked)}
                                disabled={isLoading}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                            <span className="font-medium text-gray-700">Ollama (Local)</span>
                        </label>

                        {useOllama && (
                            <div className="ml-7 space-y-3 bg-gray-50 p-3 rounded">
                                <div>
                                    <label htmlFor="ollamaUrl" className="label text-sm">
                                        Endpoint URL *
                                    </label>
                                    <input
                                        id="ollamaUrl"
                                        type="text"
                                        value={ollamaUrl}
                                        onChange={(e) => setOllamaUrl(e.target.value)}
                                        className="input-field text-sm"
                                        placeholder="http://localhost:11434/v1"
                                        disabled={isLoading}
                                    />
                                </div>
                                <div>
                                    <label htmlFor="ollamaModel" className="label text-sm">
                                        Model {loadingOllamaModels && '(Loading...)'}
                                    </label>
                                    {ollamaModels.length > 0 ? (
                                        <select
                                            id="ollamaModel"
                                            value={ollamaModel}
                                            onChange={(e) => setOllamaModel(e.target.value)}
                                            className="select-field text-sm"
                                            disabled={isLoading || loadingOllamaModels}
                                        >
                                            {ollamaModels.map((model) => (
                                                <option key={model} value={model}>
                                                    {model}
                                                </option>
                                            ))}
                                        </select>
                                    ) : (
                                        <input
                                            id="ollamaModel"
                                            type="text"
                                            value={ollamaModel}
                                            onChange={(e) => setOllamaModel(e.target.value)}
                                            className="input-field text-sm"
                                            placeholder="llama2"
                                            disabled={isLoading}
                                        />
                                    )}
                                    <p className="text-xs text-gray-500 mt-1">
                                        Download models at{' '}
                                        <a href="https://ollama.com" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                                            ollama.com
                                        </a>
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    className="btn-primary w-full"
                    disabled={isLoading || isOverLimit}
                >
                    {isLoading ? (
                        <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Translating...
                        </span>
                    ) : (
                        'Run Translation'
                    )}
                </button>
            </form>
        </div>
    );
}
