import asyncio
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models import RawTweet, EnrichedItem
from backend.cognitive.mlx_engine import mlx_engine
from backend.cognitive.hindi_prompts import construct_gemma3_prompt
from backend.cognitive.geo_resolver import HybridLocationResolver

# Configure logging
log_file = "data/gemma3_enrichment.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Gemma3EnrichmentService:
    """
    Service to enrich tweets using Gemma 3 QAT 12B via MLX.
    Uses the proven 7-Layer Cognitive Model with Hindi-first prompting.
    Reads from RawTweet, processes with MLXEngine, and writes to EnrichedItem.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.engine = mlx_engine
        # Initialize Hybrid Location Resolver (V2 Logic)
        self.location_resolver = HybridLocationResolver(enable_semantic=False) # Disable semantic for speed/dependency simplicity

    async def get_pending_tweets(self, limit: int = 10) -> List[RawTweet]:
        """
        Fetches tweets that haven't been enriched yet.
        """
        # Subquery to find IDs already in enriched_items
        subquery = select(EnrichedItem.tweet_id)
        
        query = select(RawTweet).where(RawTweet.tweet_id.not_in(subquery)).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def enrich_tweet(self, tweet: RawTweet) -> Optional[EnrichedItem]:
        """
        Enriches a single tweet using Gemma 3's 7-layer cognitive analysis.
        """
        logger.info(f"Enriching tweet {tweet.tweet_id}...")
        
        try:
            # Construct Hindi-boosted prompt
            prompt = construct_gemma3_prompt(tweet.text)
            
            # Call Gemma 3
            response_json = self.engine.generate_json(prompt)
            
            if "error" in response_json:
                logger.error(f"Failed to generate valid JSON for {tweet.tweet_id}: {response_json}")
                return None

            # Validate and extract fields
            themes = response_json.get("themes", [])
            layers = response_json.get("layers", {})
            location_candidates = response_json.get("location_candidates", {})
            
            # --- V2 Location Logic Integration ---
            # Use HybridLocationResolver to get precise hierarchy
            # We pass the raw text and extracted people (for entity inference)
            people_entities = response_json.get("people", [])
            resolved_loc, loc_conf, loc_source = self.location_resolver.resolve(tweet.text, entities=people_entities)
            
            if resolved_loc:
                # Add resolved location to candidates
                location_candidates["resolved"] = resolved_loc
                location_candidates["resolver_source"] = loc_source
                # Also add to inferred if not present
                if "inferred" not in location_candidates:
                    location_candidates["inferred"] = []
                if resolved_loc.get("canonical") not in location_candidates["inferred"]:
                    location_candidates["inferred"].append(resolved_loc.get("canonical"))
            
            # Build semantic word buckets (combining themes + layers like Phi does)
            semantic_buckets = self._build_semantic_buckets(response_json)
            
            # Map to EnrichedItem model
            enriched = EnrichedItem(
                tweet_id=tweet.tweet_id,
                themes=themes,
                event_type=response_json.get("event_type"),
                sentiment=response_json.get("sentiment"),
                location_candidates=location_candidates,
                schemes=response_json.get("schemes", []),
                communities=response_json.get("communities", []),
                people=response_json.get("people", []),
                organizations=response_json.get("organizations", []),
                layers=response_json.get("layers", {}),
                notes=response_json.get("notes"),
                confidence_score=self._estimate_confidence(response_json),
                model_version=self.engine.model_path
            )
            
            # Log the raw output in the requested format (Gemma 2 style)
            logger.info(
                f"Raw Gemma 3 Output: Notes: {response_json.get('notes')}\n\n"
                f"Domain: {layers.get('domain')}\n"
                f"Occasion: {layers.get('occasion')}\n"
                f"Action: {layers.get('action')}\n"
                f"Relationship: {layers.get('relationship')}\n"
                f"Strategy: {layers.get('strategy')}\n"
                f"Emotion: {layers.get('emotion')}\n"
                f"Audience: {layers.get('audience')}\n"
                f"People: {response_json.get('people')}\n"
                f"Organizations: {response_json.get('organizations')}\n"
                f"Locations: {location_candidates}\n"
                f"Schemes: {response_json.get('schemes')}\n"
                f"Event: {response_json.get('event_type')}\n"
                f"Confidence: {enriched.confidence_score}\n"
            )
            
            # Log the enrichment details (Structured Summary)
            logger.info(
                f"[ENRICH] {tweet.tweet_id} "
                f"themes={themes} "
                f"people={response_json.get('people')} "
                f"orgs={response_json.get('organizations')} "
                f"locs={location_candidates} "
                f"schemes={response_json.get('schemes')}"
            )
            
            logger.info(f"✅ Enriched {tweet.tweet_id} - buckets: {semantic_buckets}")
            
            return enriched

        except Exception as e:
            logger.error(f"Error enriching tweet {tweet.tweet_id}: {e}")
            return None
    
    def _build_semantic_buckets(self, response: Dict[str, Any]) -> List[str]:
        """
        Build semantic word buckets from Gemma 3 output.
        Combines themes + all 7 layers for comprehensive semantic coverage.
        """
        buckets = []
        
        # Add main themes
        buckets.extend(response.get("themes", []))
        
        # Add event type
        event = response.get("event_type")
        if event:
            buckets.append(event)
        
        # Add all 7 layers
        layers = response.get("layers", {})
        for layer_name in ["domain", "occasion", "action", "relationship", "strategy", "emotion", "audience"]:
            layer_values = layers.get(layer_name, [])
            if isinstance(layer_values, list):
                buckets.extend(layer_values)
        
        # Add entities
        buckets.extend(response.get("people", []))
        buckets.extend(response.get("organizations", []))
        buckets.extend(response.get("schemes", []))
        buckets.extend(response.get("communities", []))
        
        # Deduplicate
        return list(dict.fromkeys([b for b in buckets if b]))
    
    def _estimate_confidence(self, response: Dict[str, Any]) -> float:
        """
        Estimate confidence based on completeness of analysis.
        """
        score = 0.5  # Base score
        
        # Bonus for having themes
        if response.get("themes"):
            score += 0.1
        
        # Bonus for event type
        if response.get("event_type"):
            score += 0.1
        
        # Bonus for notes
        if response.get("notes") and len(response.get("notes", "")) > 20:
            score += 0.15
        
        # Bonus for layers
        layers = response.get("layers", {})
        if len(layers) >= 4:
            score += 0.15
        
        return min(score, 1.0)

    async def process_batch(self, limit: int = 10):
        """
        Process a batch of pending tweets.
        """
        tweets = await self.get_pending_tweets(limit)
        logger.info(f"Found {len(tweets)} pending tweets for Gemma 3 enrichment.")
        
        for tweet in tweets:
            enriched_item = await self.enrich_tweet(tweet)
            if enriched_item:
                self.db.add(enriched_item)
                await self.db.commit()
                logger.info(f"✅ Saved Gemma 3 enrichment for {tweet.tweet_id}")
            else:
                logger.warning(f"⚠️  Skipping save for {tweet.tweet_id} due to failure.")

# Standalone runner
async def run_enrichment_job(limit: int = 5):
    from backend.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        service = Gemma3EnrichmentService(session)
        await service.process_batch(limit)

if __name__ == "__main__":
    # For testing
    asyncio.run(run_enrichment_job())
