-- =============================================================================
-- TCVG Query Presets :: Real-time card retrieval for 'berserk'
-- =============================================================================


-- [1. Fast Path] Instant O(1) resolution via vector index ID
SELECT * FROM {table_name} WHERE faiss_id = ?;

-- [2. OCR Fallback] Deterministic match by set release number and card number
SELECT * FROM {table_name} WHERE set_number = ? AND collector_number = ?;

-- [3. Heuristic Fallback] Candidate pruning via frame element and crystal cost
SELECT * FROM {table_name} WHERE element = ? AND cost = ?;
