# AI Translation Benchmark - Metrics Explanation

**Author:** Zoltan Tamas Toth

This document explains the evaluation metrics used in the AI Translation Benchmark platform.

## Overview

The platform uses a multi-faceted approach to translation quality assessment, combining:
- **Reference-free metrics** (Quality Estimation) - work without a gold standard translation
- **Reference-based metrics** - require a reference translation for comparison
- **Score fusion** - weighted combination of all metrics

## Reference-Free Metrics (Quality Estimation)

These metrics evaluate translation quality without requiring a reference translation.

### 1. Language Detection

**Purpose:** Verify that the output is in the correct target language.

**How it works:**
- Uses `langdetect` library to identify the language of the translation
- Compares detected language with expected target language
- Returns confidence score

**Scoring:**
- 100 points: Correct language with high confidence (≥80%)
- Proportional: Correct language with lower confidence
- 0 points: Wrong language detected

**Weight:** 15% (configurable)

**Example:**
- Source: "Hello, world!" (English)
- Target: "¡Hola, mundo!" (Spanish)
- Detected: Spanish (99% confidence)
- Score: 100/100 ✓

---

### 2. Length Ratio

**Purpose:** Detect translations that are unusually short or long compared to the source.

**How it works:**
- Calculates ratio: `target_length / source_length`
- Compares against acceptable range (default: 0.5 - 2.0)
- Penalizes extreme ratios

**Scoring:**
- Best score: Ratio close to 1.0
- Acceptable: Within configured range (50-100 points)
- Poor: Outside range (0-50 points)

**Weight:** 10% (configurable)

**Example:**
- Source: "Hello, world!" (13 chars)
- Target: "¡Hola, mundo!" (13 chars)
- Ratio: 1.0
- Score: 100/100 ✓

---

### 3. Repetition Detection

**Purpose:** Identify excessive repetition in translations (a common failure mode).

**How it works:**
- Analyzes n-grams (2-4 words) in the translation
- Calculates repetition score based on unique vs. total n-grams
- Detects patterns like "test test test test"

**Scoring:**
- 100 points: No repetition detected
- Lower scores: Increasing repetition
- Warning triggered: Repetition score > 30%

**Weight:** 15% (configurable)

**Example:**
- Good: "This is a unique translation"
- Bad: "test test test test" (high repetition)

---

### 4. Content Preservation

**Purpose:** Ensure important content elements are preserved in translation.

**Components:**

**a) Number Preservation**
- Extracts numbers, decimals, percentages from source
- Checks if they appear in target
- Example: "$100" should remain "$100"

**b) Punctuation Preservation**
- Compares punctuation patterns
- Ensures formatting is maintained
- Example: "Hello, world!" → "¡Hola, mundo!"

**c) Named Entity Preservation**
- Identifies capitalized words (simple heuristic)
- Checks if they're preserved
- Example: "New York" should remain "New York"

**Scoring:**
- Component scores averaged
- 100 points: All elements preserved
- Proportional reduction for missing elements

**Weight:** 20% (configurable)

---

### 5. Semantic Similarity

**Purpose:** Measure cross-lingual semantic consistency between source and target.

**How it works:**
- Uses multilingual sentence embeddings (sentence-transformers)
- Default model: `paraphrase-multilingual-MiniLM-L12-v2`
- Computes cosine similarity between source and target embeddings
- Captures meaning preservation across languages

**Scoring:**
- Based on cosine similarity (0-1 range)
- Converted to 0-100 scale
- Higher similarity = better semantic preservation

**Weight:** 40% (configurable)

**Technical Details:**
- Model: 384-dimensional embeddings
- Supports 50+ languages
- Captures semantic meaning, not just word overlap

---

## Reference-Based Metrics

These metrics require a reference (gold standard) translation for comparison.

### 6. BLEU Score

**Purpose:** Measure n-gram overlap with reference translation.

**How it works:**
- Compares 1-4 gram matches between hypothesis and reference
- Applies brevity penalty for short translations
- Industry standard metric

**Scoring:** 0-100 (higher is better)

**Weight:** 30% (when reference provided)

**Note:** Currently scaffolded, full implementation in Milestone 2

---

### 7. chrF / chrF++

**Purpose:** Character-level F-score for translation quality.

**How it works:**
- Character n-gram matching
- More robust to morphological variations
- Better for non-English languages

**Scoring:** 0-100 (higher is better)

**Weight:** 35% (when reference provided)

**Note:** Currently scaffolded, full implementation in Milestone 2

---

### 8. BERTScore

**Purpose:** Embedding-based similarity with reference.

**How it works:**
- Uses contextual embeddings (BERT-based)
- Computes token-level similarity
- Returns precision, recall, F1

**Scoring:** 0-100 (F1 score)

**Weight:** 35% (when reference provided)

**Note:** Currently scaffolded, full implementation in Milestone 2

---

## Score Fusion

### Overall Score Calculation

The overall score is a **weighted average** of all enabled metrics:

```
overall_score = Σ(metric_score × metric_weight) / Σ(metric_weight)
```

### Default Weights (Reference-Free Mode)

| Metric | Weight |
|--------|--------|
| Language Detection | 15% |
| Length Ratio | 10% |
| Repetition | 15% |
| Preservation | 20% |
| Semantic Similarity | 40% |

### Interpretation

| Score Range | Quality Level |
|-------------|---------------|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| 0-59 | Poor |

### Explanation Generation

The system automatically generates explanations based on:
- Overall quality level
- Top contributing metrics
- Detected warnings

Example:
> "Good translation quality (score: 82.5/100). Top factors: Semantic Similarity, Content Preservation, Language Detection."

---

## Configuration

Metric weights can be customized in `config.yaml`:

```yaml
metrics:
  heuristics:
    language_detection:
      weight: 0.15
      enabled: true
    
    length_ratio:
      weight: 0.10
      enabled: true
      min_ratio: 0.5
      max_ratio: 2.0
    
    repetition:
      weight: 0.15
      enabled: true
    
    preservation:
      weight: 0.20
      enabled: true
  
  semantic:
    weight: 0.40
    enabled: true
    model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

---

## Warnings and Diagnostics

The system generates warnings for common issues:

| Warning | Trigger |
|---------|---------|
| Language Mismatch | Detected language ≠ target language |
| Low Confidence | Language detection confidence < 80% |
| Length Anomaly | Ratio outside acceptable range |
| High Repetition | Repetition score > 30% |
| Content Loss | Numbers, entities, or punctuation missing |
| Format Drift | Punctuation pattern significantly different |

---

## Future Enhancements

### Planned Metrics (Milestone 3+)

1. **Fluency Score**
   - Target language perplexity
   - Grammar checking (LanguageTool)

2. **Trained QE Model**
   - Feature engineering pipeline
   - XGBoost/Neural QE
   - Trained on WMT QE datasets

3. **COMET**
   - State-of-the-art learned metric
   - Requires larger model download

---

## References

- **BLEU:** Papineni et al., 2002
- **chrF:** Popović, 2015
- **BERTScore:** Zhang et al., 2020
- **Sentence-BERT:** Reimers & Gurevych, 2019
- **Quality Estimation:** Specia et al., 2018
