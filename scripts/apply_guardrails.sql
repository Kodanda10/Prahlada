
CREATE OR REPLACE FUNCTION protect_gemma3_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Allow updates ONLY to review-related columns
    -- We check if core fields are being changed
    IF (OLD.themes IS DISTINCT FROM NEW.themes OR
        OLD.layers IS DISTINCT FROM NEW.layers OR
        OLD.location_candidates IS DISTINCT FROM NEW.location_candidates OR
        OLD.schemes IS DISTINCT FROM NEW.schemes OR
        OLD.people IS DISTINCT FROM NEW.people) THEN
        RAISE EXCEPTION '🚫 ACCESS DENIED: Core Gemma 3 enrichment data is READ-ONLY. You can only update review_status, final_data, and metadata.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS gemma3_readonly_guard ON enriched_items;

CREATE TRIGGER gemma3_readonly_guard
BEFORE UPDATE ON enriched_items
FOR EACH ROW
EXECUTE FUNCTION protect_gemma3_data();
