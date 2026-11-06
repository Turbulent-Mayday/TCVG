-- =============================================================================
-- TCVG Indexing :: Optimized access paths for 'berserk'
-- =============================================================================

-- [Search Strategy 1] Normalized title index for rapid Levenshtein fuzzy matching
CREATE INDEX IF NOT EXISTS idx_{game}_name_norm ON {table_name}(name_normalized);

-- [Search Strategy 2] Bottom-strip composite index for targeted OCR routing
CREATE INDEX IF NOT EXISTS idx_{game}_set_num ON {table_name}(set_number, collector_number);

-- [Search Strategy 3] Heuristic visual attributes filter (frame color, cost, rarity)
CREATE INDEX IF NOT EXISTS idx_{game}_indirect ON {table_name}(element, cost_type, cost, rarity);
