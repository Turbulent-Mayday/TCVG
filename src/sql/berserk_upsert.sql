-- =============================================================================
-- TCVG Ingest :: Idempotent upsert pipeline for 'berserk'
-- Conflict resolution on card_uid with atomic field updates
-- =============================================================================

INSERT INTO {table_name} (
    faiss_id,
    id,
    card_uid,
    name,
    name_normalized,
    strike_weak,
    strike_medium,
    strike_strong,
    image_url,
    image_s3_key,
    image_human_key,
    details_url,
    flavor_text,
    rarity,
    rarity_image,
    set_name,
    set_number,
    collector_number,
    artist,
    element,
    cost,
    cost_type,
    hp,
    moves,
    text,
    text_images_json,
    faq_json
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
ON CONFLICT(card_uid) DO UPDATE SET
    faiss_id = excluded.faiss_id,
    id = excluded.id,
    name = excluded.name,
    name_normalized = excluded.name_normalized,
    strike_weak = excluded.strike_weak,
    strike_medium = excluded.strike_medium,
    strike_strong = excluded.strike_strong,
    image_url = excluded.image_url,
    image_s3_key = excluded.image_s3_key,
    image_human_key = excluded.image_human_key,
    details_url = excluded.details_url,
    flavor_text = excluded.flavor_text,
    rarity = excluded.rarity,
    rarity_image = excluded.rarity_image,
    set_name = excluded.set_name,
    set_number = excluded.set_number,
    collector_number = excluded.collector_number,
    artist = excluded.artist,
    element = excluded.element,
    cost = excluded.cost,
    cost_type = excluded.cost_type,
    hp = excluded.hp,
    moves = excluded.moves,
    text = excluded.text,
    text_images_json = excluded.text_images_json,
    faq_json = excluded.faq_json;
