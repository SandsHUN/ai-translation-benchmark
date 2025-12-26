"""
AI Translation Benchmark - Core Constants

Author: Zoltan Tamas Toth

This module contains all constant values used throughout the application
to avoid magic strings and ensure consistency.
"""

# API Routes
API_PREFIX = "/api"
ROUTE_HEALTH = "/health"
ROUTE_RUN = "/run"
ROUTE_RUN_BY_ID = "/run/{run_id}"
ROUTE_PROVIDERS = "/providers"

# HTTP Status Messages
MSG_HEALTH_OK = "healthy"
MSG_TRANSLATION_SUCCESS = "Translation completed successfully"
MSG_TRANSLATION_FAILED = "Translation failed"
MSG_PROVIDER_NOT_FOUND = "Provider not found"
MSG_INVALID_REQUEST = "Invalid request parameters"
MSG_RUN_NOT_FOUND = "Run not found"

# Provider Types
PROVIDER_TYPE_OPENAI = "openai"
PROVIDER_TYPE_LOCAL_OPENAI = "local_openai"
PROVIDER_TYPE_DEEPL = "deepl"
PROVIDER_TYPE_GOOGLE = "google_translate"

# Metric Names
METRIC_LANGUAGE_DETECTION = "language_detection"
METRIC_LENGTH_RATIO = "length_ratio"
METRIC_REPETITION = "repetition"
METRIC_PRESERVATION = "preservation"
METRIC_SEMANTIC_SIMILARITY = "semantic_similarity"
METRIC_BLEU = "bleu"
METRIC_CHRF = "chrf"
METRIC_BERTSCORE = "bertscore"
METRIC_OVERALL = "overall_score"

# Evaluation Categories
CATEGORY_HEURISTICS = "heuristics"
CATEGORY_SEMANTIC = "semantic"
CATEGORY_REFERENCE_BASED = "reference_based"

# Default Values
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_TEXT_LENGTH = 1000
DEFAULT_TEMPERATURE = 0.3
DEFAULT_LOG_LEVEL = "INFO"

# Score Ranges
SCORE_MIN = 0.0
SCORE_MAX = 100.0

# Length Ratio Thresholds
LENGTH_RATIO_MIN = 0.5
LENGTH_RATIO_MAX = 2.0

# Repetition Detection
MAX_NGRAM_SIZE = 4
REPETITION_THRESHOLD = 0.3

# Database
DB_TABLE_RUNS = "runs"
DB_TABLE_TRANSLATIONS = "translations"
DB_TABLE_EVALUATIONS = "evaluations"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_PREFIX = "translation_benchmark"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 30  # Keep 30 days of logs

# Export Formats
EXPORT_FORMAT_JSON = "json"
EXPORT_FORMAT_CSV = "csv"

# Language Codes (ISO 639-1)
LANG_ENGLISH = "en"
LANG_SPANISH = "es"
LANG_FRENCH = "fr"
LANG_GERMAN = "de"
LANG_ITALIAN = "it"
LANG_PORTUGUESE = "pt"
LANG_CHINESE = "zh"
LANG_JAPANESE = "ja"
LANG_KOREAN = "ko"
LANG_RUSSIAN = "ru"
LANG_ARABIC = "ar"
LANG_HINDI = "hi"

# Supported Languages List
SUPPORTED_LANGUAGES = [
    LANG_ENGLISH,
    LANG_SPANISH,
    LANG_FRENCH,
    LANG_GERMAN,
    LANG_ITALIAN,
    LANG_PORTUGUESE,
    LANG_CHINESE,
    LANG_JAPANESE,
    LANG_KOREAN,
    LANG_RUSSIAN,
    LANG_ARABIC,
    LANG_HINDI,
]

# OpenAI Models
OPENAI_MODEL_GPT4 = "gpt-4"
OPENAI_MODEL_GPT4_TURBO = "gpt-4-turbo-preview"
OPENAI_MODEL_GPT35_TURBO = "gpt-3.5-turbo"

# Embedding Models
EMBEDDING_MODEL_MULTILINGUAL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Error Messages
ERR_PROVIDER_TIMEOUT = "Provider request timed out"
ERR_PROVIDER_AUTH = "Provider authentication failed"
ERR_PROVIDER_INVALID_RESPONSE = "Provider returned invalid response"
ERR_LANGUAGE_MISMATCH = "Output language does not match target language"
ERR_EMPTY_TRANSLATION = "Translation result is empty"
ERR_TEXT_TOO_LONG = "Input text exceeds maximum length"
ERR_UNSUPPORTED_LANGUAGE = "Unsupported language code"
ERR_DATABASE_ERROR = "Database operation failed"
ERR_CONFIG_INVALID = "Invalid configuration"
ERR_RUN_NOT_FOUND = "Translation run not found"


# Warning Messages
WARN_LOW_CONFIDENCE = "Low confidence in language detection"
WARN_LENGTH_ANOMALY = "Unusual length ratio detected"
WARN_HIGH_REPETITION = "High repetition detected in translation"
WARN_CONTENT_LOSS = "Potential content loss detected"
WARN_FORMAT_DRIFT = "Format preservation issues detected"

# System Prompts
TRANSLATION_SYSTEM_PROMPT = """You are a professional translator.
Your task is to translate the following text from {source_lang} to {target_lang}.

IMPORTANT: You MUST translate to {target_lang} language. Do not translate to any other language.

Guidelines:
- Preserve the original meaning, tone, and formatting
- Maintain numbers, dates, and named entities exactly as they appear
- Provide ONLY the translation in {target_lang}
- Do NOT add any commentary, explanation, or notes
- Do NOT translate to any language other than {target_lang}"""

# File Paths
PATH_DATA_DIR = "data"
PATH_LOGS_DIR = "logs"
PATH_CONFIG_FILE = "config.yaml"
PATH_ENV_FILE = ".env"
