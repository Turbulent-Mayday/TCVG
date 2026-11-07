-- =============================================================================
-- TCVG Engine :: Auto-generated schema definition for 'berserk'
-- Inferred attributes: 27 | Target table: {table_name}
-- =============================================================================

CREATE TABLE IF NOT EXISTS {table_name} (
    faiss_id INTEGER PRIMARY KEY,
    id INTEGER,
    card_uid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_normalized TEXT NOT NULL,
    strike_weak INTEGER,
    strike_medium INTEGER,
    strike_strong INTEGER,
    image_url TEXT,
    image_s3_key TEXT,
    image_human_key TEXT,
    details_url TEXT,
    flavor_text TEXT,
    rarity TEXT,
    rarity_image TEXT,
    set_name TEXT,
    set_number INTEGER,
    collector_number TEXT,
    artist TEXT,
    element TEXT,
    cost INTEGER,
    cost_type TEXT,
    hp INTEGER,
    moves INTEGER,
    text TEXT,
    text_images_json TEXT,
    faq_json TEXT
);
