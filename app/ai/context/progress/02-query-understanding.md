# Feature: Query Understanding Layer

## What Was Done

- Created `app/services/query_understanding.py` with `QueryUnderstandingService`
- Integrated into `SearchService.search_products()` as a preprocessing step
- Pipeline: normalize → apply_synonyms → expand
- Processed query is used for both embedding generation and keyword extraction

## Why

Raw user queries often don't match product data well:
- "smart phone" (two words) won't match "smartphone" (one word) in keyword scoring
- Short queries like "tv" miss semantic context that embeddings need
- Inconsistent casing/spacing degrades both keyword and vector matching

Query understanding transforms the input before it reaches the search pipeline,
improving both the embedding vector and the keyword ILIKE matches.

## Result

| Input | Output |
|---|---|
| `"smart phone"` | `"smartphone mobile device electronics"` |
| `"tv"` | `"television tv display screen electronics"` |
| `"bike"` | `"bicycle bike cycling sports"` |
| `"laptop"` | `"laptop computer electronics"` |
| `"  GAMING  controller  "` | `"gaming controller"` |

- Synonym replacement fixes vocabulary mismatches
- Query expansion adds related terms that improve both embedding quality and keyword hit rate
- Normalization ensures consistent processing

## Issues

- Synonym and expansion dictionaries are static — must be maintained manually
- Expansion can increase the number of keyword tokens, which dilutes per-keyword scoring
  (mitigated by normalization in `_build_keyword_score_expression`)
- No handling of typos or fuzzy matching
- Multi-word synonyms are matched via regex; word-boundary issues possible for very short keys

## Next Steps

- [ ] Add more synonyms and expansions based on real query logs
- [ ] Consider category-aware expansion (e.g. "apple" → fruit vs electronics)
- [ ] Add stopword removal to `_extract_keywords` to avoid noise tokens from expansion
- [ ] Evaluate impact on search result quality with A/B metrics
- [ ] Add unit tests for `QueryUnderstandingService`
