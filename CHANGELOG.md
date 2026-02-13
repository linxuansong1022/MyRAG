# 📝 Change Log

## [2026-02-13] Gemini API JSON Parsing Fixes

### 🐛 Bug Fixes
- **JSON Parsing Error (Extra Data)**: Fixed issue where Gemini API responses contained explanatory text after the JSON object, causing `json.loads()` to fail with "Extra data" error.
- **Markdown Formatting**: Improved handling of markdown code blocks (```json ... ```) in API responses.

### 🛠️ Code Changes
1. **`rag_modules/intelligent_query_router.py`**
   - Added regex-based JSON extraction to `analyze_query()`
   - Sanitizes response content before parsing

2. **`rag_modules/hybrid_retrieval.py`**
   - Applied same regex extraction logic to `extract_query_keywords()`

3. **`rag_modules/graph_rag_retrieval.py`**
   - Applied same regex extraction logic to `_analyze_query_intent()`

### 📈 Impact
- System effectively ignores non-JSON text from LLM
- Significantly improved robustness of query analysis and keyword extraction
- Resolved `Expecting value` and `Extra data` errors in logs
