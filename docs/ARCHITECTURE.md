# AI Translation Benchmark - Architecture

**Author:** Zoltan Tamas Toth

## System Overview

The AI Translation Benchmark is a full-stack application designed to evaluate translation quality across multiple AI providers using both traditional metrics and modern machine learning approaches.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (React + Vite)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Input   │  │  Output  │  │  Model   │  │  Score   │   │
│  │  Panel   │  │  Panel   │  │  Card    │  │Breakdown │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────┐
│                      Backend API                             │
│                     (FastAPI)                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Routes                              │   │
│  │  /api/run  /api/run/{id}  /api/providers  /health   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────┬────────────┬────────────┬────────────┬───────────────┘
       │            │            │            │
   ┌───▼───┐   ┌───▼───┐   ┌────▼────┐  ┌───▼────┐
   │Provider│   │Evalua-│   │Database │  │Config  │
   │ System │   │tion   │   │(SQLite) │  │Manager │
   └───┬───┘   │Engine │   └─────────┘  └────────┘
       │       └───┬───┘
   ┌───▼───┐   ┌───▼───────────────────────┐
   │OpenAI │   │  Metrics                  │
   │Local  │   │  - Heuristics             │
   │Models │   │  - Semantic Similarity    │
   └───────┘   │  - Score Fusion           │
               └───────────────────────────┘
```

## Component Breakdown

### Frontend Layer

**Technology:** React 18, TypeScript, Vite, Tailwind CSS

**Components:**
- `InputPanel`: User input for text, language selection, and provider configuration
- `OutputPanel`: Displays results with loading and empty states
- `ModelCard`: Individual provider results with tabbed interface
- `ScoreBreakdown`: Visual representation of metric scores
- `RankingSummary`: Comparative ranking of all providers

**State Management:** TanStack Query for API state management

### Backend Layer

**Technology:** FastAPI, Python 3.11+, Pydantic, SQLAlchemy

**Core Modules:**

1. **API Layer** (`app/api/`)
   - RESTful endpoints for translation, provider info, and health checks
   - Request/response validation with Pydantic
   - Async request handling

2. **Provider System** (`app/providers/`)
   - Abstract base class for extensibility
   - OpenAI provider implementation
   - Local OpenAI-compatible provider (LM Studio, etc.)
   - Factory pattern for provider instantiation

3. **Evaluation Engine** (`app/evaluation/`)
   - **Heuristics**: Language detection, length ratio, repetition, preservation
   - **Semantic**: Cross-lingual embedding similarity
   - **Score Fusion**: Weighted combination of metrics
   - **Orchestrator**: Coordinates all evaluation steps

4. **Database Layer** (`app/db/`)
   - SQLAlchemy async ORM
   - Models: Run, Translation, Evaluation
   - Repository pattern for data access

5. **Core Infrastructure** (`app/core/`)
   - Configuration management (env + YAML)
   - Constants (no magic strings)
   - Structured logging with daily rotation

### Data Flow

1. **Translation Request:**
   ```
   User Input → API Endpoint → Provider Factory → Parallel Translation Calls
   ```

2. **Evaluation:**
   ```
   Translation Results → Evaluator → Metrics (Heuristics + Semantic) → Score Fusion
   ```

3. **Storage:**
   ```
   Run + Translations + Evaluations → Repository → SQLite Database
   ```

4. **Response:**
   ```
   Results + Evaluations + Rankings → API Response → Frontend Display
   ```

## Key Design Patterns

### Provider Pattern
- Abstract base class `TranslatorProvider`
- Concrete implementations for each provider type
- Factory for instantiation
- Easy to extend with new providers

### Repository Pattern
- Centralized data access layer
- Abstracts database operations
- Supports testing with mock repositories

### Score Fusion
- Configurable metric weights
- Weighted average calculation
- Explanation generation

## Extensibility Points

### Adding New Providers
1. Implement `TranslatorProvider` interface
2. Register in provider factory
3. Add configuration to `config.yaml`

### Adding New Metrics
1. Create metric class in `app/evaluation/`
2. Integrate into `Evaluator`
3. Add weight configuration
4. Update score fusion

### Adding Reference-Based Metrics
- BLEU, chrF, BERTScore implementations ready
- Requires reference translation input
- Already scaffolded in evaluation system

## Configuration

### Environment Variables (`.env`)
- API keys (OpenAI)
- Database URL
- Server settings
- CORS origins

### YAML Configuration (`config.yaml`)
- Provider definitions
- Metric weights
- Language support
- Timeouts and limits

## Security Considerations

- API keys never committed to git
- CORS configuration for frontend
- Input validation with Pydantic
- SQL injection prevention (ORM)
- Timeout protection for provider calls

## Performance Optimizations

- Async/await throughout
- Parallel provider calls
- Lazy loading of ML models
- Database connection pooling
- Frontend code splitting (Vite)

## Monitoring & Logging

- Structured logging with timestamps
- Daily log rotation (30 days retention)
- Key operations logged:
  - Translation requests
  - Provider calls
  - Evaluation runs
  - Database operations
- Health check endpoint for uptime monitoring
