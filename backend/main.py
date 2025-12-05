import os
print("DEBUG: Imported os")
import json
from pathlib import Path
from typing import Any, Optional
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
print("DEBUG: Imported fastapi")
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from contextlib import asynccontextmanager
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
print("DEBUG: Imported standard libs")

load_dotenv()
print("DEBUG: Loaded dotenv")

from . import models, schemas
print("DEBUG: Imported models, schemas")
from .database import engine, get_db_session, AsyncSessionLocal
print("DEBUG: Imported database")
# from .vector_store import get_vector_store  # TEMPORARILY DISABLED - hangs on SentenceTransformer load
# print("DEBUG: Imported vector_store")
from .auth import authenticate_user, create_access_token, get_current_user, ensure_default_admin
print("DEBUG: Imported auth")

# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    # On startup:
    print("DEBUG: Application startup begin...")
    # Initialize database tables (if they don't exist)
    print("DEBUG: Connecting to database...")
    try:
        async with engine.begin() as conn:
            print("DEBUG: Database connected. Creating tables...")
            # await conn.run_sync(models.Base.metadata.drop_all) # Use for development reset
            await conn.run_sync(models.Base.metadata.create_all)
            print("DEBUG: Tables created.")
    except Exception as e:
        print(f"DEBUG: Database connection failed: {e}")
        raise e

    print("DEBUG: Database initialization complete.")
    # Initialize default admin
    print("DEBUG: Ensuring default admin...")
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if admin_username and admin_password:
        async with AsyncSessionLocal() as db:
            await ensure_default_admin(db, admin_username, admin_password)
        print("DEBUG: Default admin ensured.")
    else:
        print("WARNING: ADMIN_USERNAME/ADMIN_PASSWORD not set. No default admin user provisioned.")
    
    # Initialize vector store on startup (lazy import)
    print("DEBUG: Initializing vector store ...")
    vector_store = None # Initialize to None
    try:
        from .vector_store import get_vector_store
        vector_store = get_vector_store()
        print("Vector store is ready.")
    except Exception as e:
        import traceback
        print(f"ERROR: Vector store initialization failed:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        print("Application will continue, but vector search features may not work.")
        # Don't raise - allow app to start so we can see full logs

    # Initialize Cognitive Engine
    print("Initializing Cognitive Engine...")
    try:
        from .cognitive.interface import CognitiveInterface
        cognitive_interface = CognitiveInterface()
        app.state.cognitive_interface = cognitive_interface
        print("DEBUG: Cognitive Interface initialized.")

        # Run initial vector indexing if the store is empty
        if vector_store and (vector_store.index is None or vector_store.index.ntotal == 0):
            print("DEBUG: Vector store is empty. Running initial indexing...")
            # vector_store already imported above
            # vector_store = get_vector_store()  # No need to call again
            await cognitive_interface.trigger_vector_indexing(vector_store)
            print("DEBUG: Initial vector indexing complete.")
        else:
            print("DEBUG: Vector store already contains data or is not initialized. Skipping initial indexing.")

    except Exception as e:
        print(f"WARNING: Cognitive Interface initialization failed: {e}")
        app.state.cognitive_interface = None

    # Initialize Phi 3.5 Cognitive Interface
    print("Initializing Phi 3.5 Cognitive Interface...")
    try:
        from .cognitive import configure_cognitive_interface, get_cognitive_interface
        phi_enabled = os.getenv("PHI_ENABLED", "false").lower() == "true"
        phi_base_url = os.getenv("PHI_BASE_URL", "http://localhost:11434")
        phi_model = os.getenv("PHI_MODEL", "phi3.5")
        
        configure_cognitive_interface(
            phi_enabled=phi_enabled,
            phi_base_url=phi_base_url,
            phi_model=phi_model
        )
        app.state.cognitive_interface = get_cognitive_interface()
        
        if phi_enabled:
            print(f"✅ Phi 3.5 Cognitive Interface enabled (model: {phi_model}, url: {phi_base_url})")
        else:
            print("⚠️ Phi 3.5 Cognitive Interface disabled (set PHI_ENABLED=true to enable)")
    except Exception as e:
        print(f"WARNING: Phi 3.5 Cognitive Interface initialization failed: {e}")
        app.state.cognitive_interface = None
    
    yield  # Application is now running
    
    # On shutdown:
    print("🛑 Shutting down...")
    try:
        vector_store = get_vector_store()
        vector_store.save()  # Save the FAISS index to disk
    except Exception as e:
        print(f"Warning: Failed to save vector store during shutdown: {e}")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Project Dhruv API",
    description="Backend for the Social Media Analytics Dashboard.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware Setup ---
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Project Dhruv API is running"}

# Use absolute path relative to this file's location
CONFIG_FILE = Path(__file__).parent / "data" / "config.json"

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Default config
    return {
        "titles": {
            "app_title": "सोशल मीडिया एनालिटिक्स",
            "app_subtitle": "छत्तीसगढ़ शासन",
            "home_tab": "होम",
            "review_tab": "समीक्षा",
            "analytics_tab": "एनालिटिक्स",
            "control_hub_tab": "कंट्रोल हब"
        },
        "modules": {
            "analytics": True,
            "review": True,
            "control_hub": True,
            # Add other defaults as needed to match frontend expectations
            "home_header": True,
            "home_filters": True,
            "home_table": True,
            "review_header": True,
            "review_queue": True,
            "review_ai_assistant": True,
            "review_semantic_search": True,
            "review_metrics": True,
            "analytics_header": True,
            "analytics_summary": True,
            "analytics_geo": True,
            "analytics_tour": True,
            "analytics_development": True,
            "analytics_outreach": True,
            "analytics_schemes": True,
            "analytics_target_groups": True,
            "analytics_thematic": True,
            "analytics_raigarh": True,
            "controlhub_header_systemhealth": True,
            "controlhub_grid_analytics_sync": True,
            "controlhub_panel_title_editor": True,
            "controlhub_panel_api_health": True
        }
    }

def save_config(config_data):
    try:
        # Ensure the parent directory exists
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

@app.get("/api/config")
def get_config():
    """
    Returns the UI configuration.
    """
    return load_config()

class ConfigUpdate(BaseModel):
    section: str
    key: str
    value: Any

@app.post("/api/config")
def update_config(update: ConfigUpdate):
    """
    Updates a specific configuration setting.
    """
    config = load_config()
    
    if update.section not in config:
        config[update.section] = {}
        
    config[update.section][update.key] = update.value
    save_config(config)
    
    return {"status": "success", "config": config}

@app.get("/api/health/system")
def get_system_health():
    """
    Returns system health statistics.
    """
    try:
        import psutil
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
    except ImportError:
        cpu_usage = 45.0  # Mock value
        memory_usage = 60.0  # Mock value

    # Check Phi 3.5 / Cognitive Interface status
    phi_status = {"status": "down", "details": "Not initialized"}
    cognitive_interface = getattr(app.state, "cognitive_interface", None)
    if cognitive_interface:
        try:
            readiness = cognitive_interface.check_cognitive_readiness()
            if readiness.get("phi_3_5_available"):
                phi_status = {"status": "up", "details": "Phi 3.5 Ready"}
            elif readiness.get("phi_3_5_enabled"):
                phi_status = {"status": "degraded", "details": "Enabled but not responding"}
            else:
                phi_status = {"status": "disabled", "details": "Disabled by configuration"}
        except Exception:
            phi_status = {"status": "error", "details": "Health check failed"}

    return {
        "status": "healthy",
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "memory_total_gb": 16, # Mock value
        "parser_uptime_seconds": 3600, # Mock value
        "p95_latency_ms": 120,
        "api_error_rate": 0.5,
        "services": {
            "ollama": {"status": "up", "details": "Running"},
            "cognitive_engine": {"status": "up", "details": "Ready"},
            "phi_3_5": phi_status,
            "database_file": {"status": "up", "details": "Connected"},
            "mapbox_integration": {"status": "up", "details": "Active"}
        }
    }

@app.get("/api/health/analytics")
def get_analytics_health():
    """
    Returns analytics health statistics.
    """
    import time
    return {
        "data_freshness": {
            "status": "fresh",
            "last_updated": int(time.time()),
            "source": "PostgreSQL"
        },
        "modules": {
            "controlhub_header_systemhealth": {"status": "fresh", "cache_hit": True},
            "controlhub_grid_analytics_sync": {"status": "fresh", "cache_hit": False}
        }
    }

@app.get("/api/analytics/event-types")
async def get_analytics_event_types(
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Returns event type distribution for analytics.
    """
    """
    Returns event type distribution for analytics.
    Aggregates from approved events' final_data.
    """
    # Query for approved events
    query = (
        select(
            models.ParsedEvent.final_data['event_type'].astext.label('name'),
            func.count(models.ParsedEvent.id).label('value')
        )
        .where(models.ParsedEvent.review_status == 'approved')
        .group_by(text("1"))
        .order_by(text("2 DESC"))
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        # Fallback to pending events if no approved data yet (for demo purposes)
        query = (
            select(
                models.ParsedEvent.event_type.label('name'),
                func.count(models.ParsedEvent.id).label('value')
            )
            .group_by(models.ParsedEvent.event_type)
            .order_by(text("2 DESC"))
        )
        result = await db.execute(query)
        rows = result.all()

    return [{"name": row.name or "Unknown", "value": row.value} for row in rows]

@app.get("/api/analytics/districts")
async def get_analytics_districts(
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Returns district-wise data for analytics.
    """
    """
    Returns district-wise data for analytics.
    Aggregates from approved events' final_data.
    """
    # Query for approved events
    query = (
        select(
            models.ParsedEvent.final_data['location']['district'].astext.label('name'),
            func.count(models.ParsedEvent.id).label('value')
        )
        .where(models.ParsedEvent.review_status == 'approved')
        .group_by(text("1"))
        .order_by(text("2 DESC"))
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        # Fallback to pending events (using locations column)
        # Note: locations is JSONB, structure might vary, assuming simple extraction for now
        # Or just return empty to encourage approval
        return []

    return [{"name": row.name or "Unknown", "value": row.value} for row in rows]


@app.get("/api/geo/children")
async def get_geo_children(
    parentId: Optional[str] = None,
    level: str = "state", # state, district, block
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Returns child geographic entities for a given parent.
    """
    # Load hierarchy data
    geo_file = Path(__file__).parent / "geo_hierarchy.json"
    data = {}
    if geo_file.exists():
        try:
            with open(geo_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading geo hierarchy: {e}")
            
    children = []
    
    if level == "state":
        # Return all districts
        # In a real app, we'd filter by state if we had multiple
        districts = data.get("districts", {}).keys()
        children = [{"id": d, "name": d, "type": "DISTRICT"} for d in districts]
        
    elif level == "district":
        # Return blocks for the district
        if parentId:
             # Handle case sensitivity or mapping if needed. For now direct lookup.
             # The frontend sends "Raigarh", "Bilaspur" etc.
             district_data = data.get("districts", {}).get(parentId)
             if district_data:
                 blocks = district_data.get("blocks", [])
                 children = [{"id": b, "name": b, "type": "BLOCK"} for b in blocks]
                 
    elif level == "block":
        # Return villages for the block
        if parentId:
            villages = data.get("blocks", {}).get(parentId, [])
            # If no specific villages found, generate some generic ones or return empty
            if not villages:
                 # Fallback to generic if not in mock data
                 children = []
            else:
                 children = [{"id": v, "name": v, "type": "VILLAGE"} for v in villages]

    return children


@app.post("/api/auth/login", response_model=schemas.AuthResponse)
async def login(payload: schemas.AuthRequest, db: AsyncSession = Depends(get_db_session)):
    user = await authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(
        {"sub": user.username, "uid": user.id, "roles": user.roles or []}
    )
    user_payload = schemas.AuthUser.model_validate(user)
    return schemas.AuthResponse(token=token, user=user_payload)


@app.get("/api/auth/verify", response_model=schemas.AuthUser)
async def verify_token(
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Verifies the current token and returns user details.
    """
    return schemas.AuthUser.model_validate(user)


@app.get("/api/stats", response_model=schemas.StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Provides real-time summary statistics from the database.
    """
    total_tweets_query = select(func.count(models.RawTweet.tweet_id))
    parsed_success_query = select(func.count(models.RawTweet.tweet_id)).where(models.RawTweet.processing_status == 'processed')
    pending_query = select(func.count(models.RawTweet.tweet_id)).where(models.RawTweet.processing_status == 'pending')
    errors_query = select(func.count(models.RawTweet.tweet_id)).where(models.RawTweet.processing_status == 'failed')

    total_tweets_res = await db.execute(total_tweets_query)
    parsed_success_res = await db.execute(parsed_success_query)
    pending_res = await db.execute(pending_query)
    errors_res = await db.execute(errors_query)

    return {
        "total_tweets": total_tweets_res.scalar_one(),
        "parsed_success": parsed_success_res.scalar_one(),
        "pending": pending_res.scalar_one(),
        "errors": errors_res.scalar_one(),
    }

@app.get("/api/events", response_model=list[schemas.EventResponse])
async def get_events(
    status: Optional[str] = None,
    enriched_only: bool = True, # Default to True for Review UX focus
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Returns the most recent parsed events joined with their raw tweet metadata.
    Supports optional filtering by raw tweet processing status (e.g. status=FAILED).
    """
    status_map = {
        "failed": "failed",
        "error": "failed",
        "pending": "pending",
        "pending_retry": "pending_retry",
        "success": "processed",
        "processed": "processed",
        "completed": "processed"
    }
    normalized_status = status.lower() if status else None
    status_filter = status_map.get(normalized_status) if normalized_status else None

    query = (
        select(models.ParsedEvent, models.RawTweet, models.EnrichedItem)
        .join(models.RawTweet, models.RawTweet.tweet_id == models.ParsedEvent.tweet_id, isouter=True)
        .join(models.EnrichedItem, models.EnrichedItem.tweet_id == models.ParsedEvent.tweet_id, isouter=True)
        .order_by(models.ParsedEvent.parsed_at.desc())
        .limit(3000)
    )
    if status_filter:
        query = query.where(models.RawTweet.processing_status == status_filter)
        
    if enriched_only:
        query = query.where(models.EnrichedItem.tweet_id != None)
    
    # Filter out replies (starting with @) and retweets (starting with RT @)
    # Only include original tweets
    query = query.where(
        ~models.RawTweet.text.like('@%')  # Exclude replies
    ).where(
        ~models.RawTweet.text.like('RT @%')  # Exclude retweets
    )

    results = await db.execute(query)
    rows = results.all()

    def as_list(value):
        if not value:
            return []
        if isinstance(value, list):
            return [item for item in value if item]
        return [value]

    def resolve_locations(categories: dict, stored_locations: list[str] | None):
        names: list[str] = []
        cat_locations = categories.get("locations") if categories else None
        if isinstance(cat_locations, list):
            for loc in cat_locations:
                if isinstance(loc, str):
                    names.append(loc)
                elif isinstance(loc, dict):
                    label = loc.get("name") or loc.get("text") or loc.get("value")
                    if label:
                        names.append(label)
        if stored_locations:
            names.extend([loc for loc in stored_locations if loc])
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        return ", ".join(unique) if unique else "Unknown"

    def map_status(raw_status: Optional[str]):
        if not raw_status:
            return "SUCCESS"
        mapping = {
            "processed": "SUCCESS",
            "pending": "PENDING",
            "pending_retry": "PENDING",
            "failed": "FAILED"
        }
        return mapping.get(raw_status.lower(), "SUCCESS")

    # Word bucket definitions for dynamic extraction
    WORD_BUCKET_KEYWORDS = {
        "कृषि": ["किसान", "कृषि", "धान", "फसल", "बीज", "खाद", "सिंचाई", "MSP", "समर्थन मूल्य"],
        "शिक्षा": ["शिक्षा", "स्कूल", "कॉलेज", "विद्यार्थी", "छात्र", "शिक्षक", "परीक्षा"],
        "स्वास्थ्य": ["स्वास्थ्य", "अस्पताल", "इलाज", "डॉक्टर", "दवा", "मेडिकल", "एम्बुलेंस"],
        "बुनियादी_ढांचा": ["सड़क", "बिजली", "पानी", "निर्माण", "पुल", "भवन", "रेलवे"],
        "कल्याण": ["राशन", "पेंशन", "आवास", "गरीब", "कल्याण", "सहायता", "अनुदान"],
        "शासन": ["प्रशासन", "योजना", "बैठक", "समीक्षा", "निरीक्षण", "उद्घाटन", "लोकार्पण"],
        "सुरक्षा": ["पुलिस", "नक्सल", "सुरक्षा", "कानून", "अपराध", "गिरफ्तार", "जवान"],
        "संस्कृति": ["संस्कृति", "त्योहार", "परंपरा", "मेला", "महोत्सव", "कला", "पर्यटन"],
        "रोजगार": ["रोजगार", "नौकरी", "भर्ती", "स्वरोजगार", "कौशल", "प्रशिक्षण"],
        "विकास": ["विकास", "प्रगति", "सौगात", "आधारशिला", "विकसित"]
    }

    def extract_word_buckets_from_text(text: str) -> list:
        """Dynamically extract word buckets from tweet text."""
        if not text:
            return []
        buckets = []
        for bucket_name, keywords in WORD_BUCKET_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                buckets.append(bucket_name)
        return buckets

    response: list[dict] = []
    for parsed_event, raw_tweet, enriched_item in rows:
        categories = parsed_event.categories if isinstance(parsed_event.categories, dict) else {}
        event_types = as_list(categories.get("event") or parsed_event.event_type)
        scheme_tags = as_list(categories.get("schemes") or parsed_event.schemes_mentioned)
        raw_text = (
            raw_tweet.text
            if raw_tweet and raw_tweet.text
            else categories.get("raw_text")
            or categories.get("clean_text")
            or ""
        )
        clean_text = (
            categories.get("clean_text")
            or categories.get("summary")
            or raw_text
        )
        location_text = resolve_locations(categories, parsed_event.locations)
        
        # Extract people
        people = as_list(categories.get("people") or parsed_event.people_mentioned)
        
        # Word buckets - try categories first, then extract dynamically from text
        word_buckets = as_list(
            categories.get("keywords") or 
            categories.get("hashtags") or 
            categories.get("word_buckets")
        )
        if not word_buckets and raw_text:
            word_buckets = extract_word_buckets_from_text(raw_text)

        log_entries = [f"parsed_at={parsed_event.parsed_at.isoformat()}"]
        if raw_tweet and raw_tweet.processing_status:
            log_entries.append(f"processing_status={raw_tweet.processing_status}")

        # MERGE LOGIC: Prefer LLM-enriched top-level columns over V2 parser categories
        # We construct the enriched_data dictionary BEFORE appending to the response list
        enriched_data = (parsed_event.categories or {}).copy()
        
        # 1. Event Type
        if parsed_event.event_type:
            enriched_data["event_type"] = parsed_event.event_type
        
        # 2. People
        if parsed_event.people_mentioned:
            enriched_data["people_canonical"] = parsed_event.people_mentioned
        
        # 3. Schemes
        if parsed_event.schemes_mentioned:
            enriched_data["schemes_mentioned"] = parsed_event.schemes_mentioned
        
        # 4. Word Buckets
        if parsed_event.word_buckets:
            enriched_data["word_buckets"] = parsed_event.word_buckets
            # Preserve parser-provided communities; expose LLM buckets separately to avoid overwriting parser hierarchy/analytics
            enriched_data.setdefault("communities", categories.get("communities") if categories else [])
            enriched_data["llm_communities"] = parsed_event.word_buckets

        # 5. Locations
        if parsed_event.locations:
            enriched_data["enriched_locations"] = parsed_event.locations

        # --- GEMMA 3 ENRICHMENT OVERRIDE ---
        if enriched_item:
            log_entries.append("enriched_by_gemma3")
            if enriched_item.event_type:
                enriched_data["event_type"] = enriched_item.event_type
                event_types = [enriched_item.event_type] # Update display list too
            
            if enriched_item.people:
                enriched_data["people_canonical"] = enriched_item.people
                people = enriched_item.people # Update display list
                
            if enriched_item.schemes:
                enriched_data["schemes_mentioned"] = enriched_item.schemes
                scheme_tags = enriched_item.schemes # Update display list
                
            if enriched_item.themes:
                enriched_data["word_buckets"] = enriched_item.themes
                enriched_data["llm_communities"] = enriched_item.themes
                word_buckets = enriched_item.themes # Update display list
                
            if enriched_item.location_candidates:
                enriched_data["enriched_locations"] = enriched_item.location_candidates
                # Update location_text if resolved location exists
                if isinstance(enriched_item.location_candidates, dict):
                    resolved = enriched_item.location_candidates.get("resolved")
                    if resolved and isinstance(resolved, dict):
                        loc_name = resolved.get("canonical") or resolved.get("name")
                        if loc_name:
                            location_text = loc_name
        
        # 6. Organizations (No top-level column, keep V2 data or use word_buckets if appropriate)
        # enriched_data["organizations"] = ... (Left as V2 for now)

        # --- FINAL DATA OVERRIDE (HUMAN REVIEW) ---
        if parsed_event.review_status == 'approved' and parsed_event.final_data:
            log_entries.append("final_data_override")
            final = parsed_event.final_data
            
            # Override all fields present in final_data
            if final.get("event_type"):
                enriched_data["event_type"] = final["event_type"]
                event_types = as_list(final["event_type"])
            
            if final.get("people"):
                enriched_data["people_canonical"] = final["people"]
                people = as_list(final["people"])
                
            if final.get("schemes"):
                enriched_data["schemes_mentioned"] = final["schemes"]
                scheme_tags = as_list(final["schemes"])
                
            if final.get("communities"):
                enriched_data["communities"] = final["communities"]
                # Also update word buckets if communities are treated as such
                enriched_data["llm_communities"] = final["communities"]
                word_buckets = as_list(final["communities"])
                
            if final.get("location"):
                enriched_data["enriched_locations"] = final["location"]
                # Update location text
                loc = final["location"]
                if isinstance(loc, dict):
                    # Construct readable location string from hierarchy
                    parts = [
                        loc.get("ulb"), 
                        loc.get("village"), 
                        loc.get("district"),
                        loc.get("state")
                    ]
                    location_text = ", ".join([p for p in parts if p]) or location_text
                elif isinstance(loc, list):
                     location_text = ", ".join([str(l) for l in loc])

        response.append({
            "tweet_id": parsed_event.tweet_id,
            "created_at": raw_tweet.created_at if raw_tweet and raw_tweet.created_at else parsed_event.parsed_at,
            "raw_text": raw_text,
            "clean_text": clean_text,
            "event_type": event_types,
            "location_text": location_text,
            "scheme_tags": scheme_tags,
            "people_mentioned": people,
            "word_buckets": parsed_event.word_buckets or word_buckets,
            "parsing_status": map_status(raw_tweet.processing_status if raw_tweet else None),
            "logs": log_entries or ["Loaded from parsed_events"],
            "review_status": parsed_event.review_status,
            "needs_review": parsed_event.needs_review,
            # Pass through richer parsed data for review UI/NLQ
            "parsed_data_v8": enriched_data,
            "metadata_v8": parsed_event.gemini_metadata or {}
        })

    return response


# ============================================================================
# Review Arbitration Endpoints (Parser vs LLM)
# ============================================================================

@app.get("/api/review/compare", response_model=schemas.ComparisonResponse)
async def get_review_comparison(
    tweet_id: str,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Get Parser vs LLM comparison for a specific tweet.
    Returns structured comparison showing conflicts and confidence scores.
    """
    # Fetch parsed event
    query = select(models.ParsedEvent).where(models.ParsedEvent.tweet_id == tweet_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Tweet {tweet_id} not found")
    
    # Fetch EnrichedItem (Gemma 3)
    enriched_query = select(models.EnrichedItem).where(models.EnrichedItem.tweet_id == tweet_id)
    enriched_result = await db.execute(enriched_query)
    enriched_item = enriched_result.scalar_one_or_none()

    # Fetch raw tweet for text
    raw_query = select(models.RawTweet).where(models.RawTweet.tweet_id == tweet_id)
    raw_result = await db.execute(raw_query)
    raw_tweet = raw_result.scalar_one_or_none()
    raw_text = raw_tweet.text if raw_tweet else ""
    
    # Build comparison object
    comparison = {}
    categories = event.categories or {}
    
    # Helper to create comparison
    def make_comparison(parser_val, llm_val, parser_conf=1.0, llm_conf=0.85):
        return schemas.FieldComparison(
            parser=schemas.EngineOutput(
                value=parser_val,
                confidence=parser_conf,
                source="parser_v2"
            ),
            llm=schemas.EngineOutput(
                value=llm_val,
                confidence=llm_conf,
                source="gemma_3_enrichment" if enriched_item else "legacy_llm"
            ),
            conflict=(parser_val != llm_val)
        )
    
    # EVENT TYPE
    parser_event = categories.get('event_type') or (categories.get('event', [None])[0] if isinstance(categories.get('event'), list) else categories.get('event'))
    llm_event = enriched_item.event_type if enriched_item else event.event_type
    comparison['event_type'] = make_comparison(
        parser_event,
        llm_event,
        parser_conf=0.9,
        llm_conf=enriched_item.confidence_score if enriched_item else (event.overall_confidence or 0.85)
    )
    
    # PEOPLE
    parser_people = categories.get('people', [])
    if not isinstance(parser_people, list):
        parser_people = [parser_people] if parser_people else []
    llm_people = enriched_item.people if enriched_item else (event.people_mentioned or [])
    comparison['people'] = make_comparison(
        parser_people,
        llm_people,
        parser_conf=0.8,
        llm_conf=0.9
    )
    
    # SCHEMES
    parser_schemes = categories.get('schemes', [])
    if not isinstance(parser_schemes, list):
        parser_schemes = [parser_schemes] if parser_schemes else []
    llm_schemes = enriched_item.schemes if enriched_item else (event.schemes_mentioned or [])
    comparison['schemes'] = make_comparison(
        parser_schemes,
        llm_schemes
    )
    
    # COMMUNITIES
    parser_communities = categories.get('communities', [])
    if not isinstance(parser_communities, list):
        parser_communities = [parser_communities] if parser_communities else []
    llm_communities = enriched_item.themes if enriched_item else (event.word_buckets or [])
    comparison['communities'] = make_comparison(
        parser_communities,
        llm_communities
    )
    
    # LOCATION (simplified)
    parser_loc = categories.get('location', {}) if isinstance(categories.get('location'), dict) else {}
    llm_locs = enriched_item.location_candidates if enriched_item else (event.locations or [])
    comparison['location'] = make_comparison(
        parser_loc,
        llm_locs
    )
    
    return schemas.ComparisonResponse(
        tweet_id=tweet_id,
        raw_text=raw_text,
        comparison=comparison
    )


@app.post("/api/review/ask-ai", response_model=schemas.AskAIResponse)
async def ask_ai(
    payload: schemas.AskAIRequest,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Ask AI about cognitive reasoning for a tweet.
    Uses cognitive_view from LLM enrichment process.
    """
    # Fetch parsed event with cognitive_view
    query = select(models.ParsedEvent).where(models.ParsedEvent.tweet_id == payload.tweet_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Tweet {payload.tweet_id} not found")
    
    # Fetch EnrichedItem (Gemma 3)
    enriched_query = select(models.EnrichedItem).where(models.EnrichedItem.tweet_id == payload.tweet_id)
    enriched_result = await db.execute(enriched_query)
    enriched_item = enriched_result.scalar_one_or_none()
    
    # Extract cognitive data
    cognitive_view = event.cognitive_view or {}
    word_buckets = event.word_buckets or []
    
    # Override with Gemma 3 data if available
    if enriched_item:
        # EnrichedItem doesn't have a direct "cognitive_view" JSON, but has "layers" and "notes"
        # We can construct a synthetic cognitive view or just use notes.
        reasoning = enriched_item.notes or "Gemma 3 Analysis Available"
        confidence = enriched_item.confidence_score
        word_buckets = enriched_item.themes or []
        
        # Add layers to cognitive view for frontend inspection
        if enriched_item.layers:
            cognitive_view = enriched_item.layers
            cognitive_view['reasoning'] = reasoning # Ensure reasoning key exists
    else:
        reasoning = cognitive_view.get('reasoning', 'No detailed reasoning available.')
        confidence = cognitive_view.get('confidence', event.overall_confidence or 0.0)
    
    # Construct answer based on question
    question_lower = payload.question.lower()
    answer = ""
    
    if 'why' in question_lower or 'reasoning' in question_lower:
        answer = f"Cognitive Analysis (Gemma 3): {reasoning}"
        if enriched_item and enriched_item.layers:
             answer += f"\n\nLayers: {json.dumps(enriched_item.layers, indent=2, ensure_ascii=False)}"
    elif 'confidence' in question_lower:
        answer = f"The LLM has {confidence*100:.1f}% confidence in this analysis. Reasoning: {reasoning}"
    elif 'people' in question_lower or 'person' in question_lower:
        people = enriched_item.people if enriched_item else event.people_mentioned
        answer = f"People mentioned: {people}. {reasoning}"
    elif 'scheme' in question_lower:
        schemes = enriched_item.schemes if enriched_item else event.schemes_mentioned
        answer = f"Schemes identified: {schemes}. {reasoning}"
    else:
        # Generic answer
        answer = f"{reasoning}\n\nWord Buckets: {', '.join(word_buckets) if word_buckets else 'None'}"
    
    return schemas.AskAIResponse(
        answer=answer,
        sources=[
            {"type": "cognitive_view", "data": cognitive_view},
            {"type": "word_buckets", "data": word_buckets}
        ],
        confidence=confidence if isinstance(confidence, float) else 0.85
    )


@app.post("/api/events/approve")
async def approve_event_with_feedback(
    payload: schemas.ApprovalRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Approve a tweet with arbitration feedback (Parser vs LLM choices).
    Saves final_data (golden record) and feedback_log.
    Triggers Cognitive Engine for manual corrections.
    """
    # Fetch event
    query = select(models.ParsedEvent).where(models.ParsedEvent.tweet_id == payload.tweet_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Tweet {payload.tweet_id} not found")
    
    # Update event with final approved data
    event.final_data = payload.final_data
    event.feedback_log = {k: v.dict() for k, v in payload.feedback.items()}
    
    if payload.exclude_from_analytics:
        event.review_status = "rejected"
    else:
        event.review_status = "approved"

    event.reviewed_at = datetime.datetime.utcnow()
    event.reviewed_by = user.username
    event.needs_review = False
    
    # ALSO Update EnrichedItem if it exists
    # Note: EnrichedItem does not have review status fields, so we only update if we decide to add them later.
    # For now, ParsedEvent is the SSOT for review status.
    # query_enriched = select(models.EnrichedItem).where(models.EnrichedItem.tweet_id == payload.tweet_id)
    # result_enriched = await db.execute(query_enriched)
    # enriched_item = result_enriched.scalar_one_or_none()
    
    # if enriched_item:
    #     pass 
          # enriched_item.review_status = event.review_status
          # enriched_item.reviewed_at = event.reviewed_at
          # enriched_item.reviewed_by = event.reviewed_by
          # enriched_item.final_data = payload.final_data
    
    await db.commit()
    
    # Trigger Cognitive Engine for Manual Corrections
    engine = getattr(app.state, "cognitive_interface", None)
    if engine:
        for field, feedback in payload.feedback.items():
            if feedback.choice == 'manual':
                # Construct correction payload
                old_val = event.categories.get(field) if event.categories else None
                new_val = payload.final_data.get(field)
                
                correction_data = {
                    "field": field,
                    "old_value": old_val,
                    "new_value": new_val,
                    "source": "human_review"
                }
                
                # Run in background
                background_tasks.add_task(
                    engine.process_correction,
                    tweet_id=payload.tweet_id,
                    tweet_text=event.raw_text,
                    old_data=event.categories or {},
                    correction=correction_data
                )

    return {"status": event.review_status, "tweet_id": payload.tweet_id}


@app.post("/api/events/skip")
async def skip_event(
    payload: schemas.SkipRequest,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Skip a tweet review.
    """
    query = select(models.ParsedEvent).where(models.ParsedEvent.tweet_id == payload.tweet_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Tweet {payload.tweet_id} not found")
        
    event.review_status = "skipped"
    event.reviewed_at = datetime.datetime.utcnow()
    event.reviewed_by = user.username
    event.needs_review = False
    
    await db.commit()
    return {"status": "skipped", "tweet_id": payload.tweet_id}

# ============================================================================
@app.get("/api/analytics/{chart_type}", response_model=list[schemas.AnalyticsDataPoint])
async def get_analytics_data(
    chart_type: str,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Provides aggregated data for analytics charts.
    """
    if chart_type == "event-types":
        # Use final_data (Golden Record) for approved tweets
        query = text("""
            SELECT 
                jsonb_array_elements_text(
                    CASE 
                        WHEN final_data IS NOT NULL AND final_data->'event_type' IS NOT NULL THEN 
                            CASE 
                                WHEN jsonb_typeof(final_data->'event_type') = 'array' THEN final_data->'event_type'
                                ELSE jsonb_build_array(final_data->'event_type')
                            END
                        ELSE categories->'event'
                    END
                ) as name, 
                COUNT(*) as value 
            FROM parsed_events 
            WHERE review_status = 'approved'
            GROUP BY name
            ORDER BY value DESC
            LIMIT 10;
        """)
        result = await db.execute(query)
        return result.mappings().all()
        
    if chart_type == "districts":
        query = text("""
            SELECT 
                jsonb_array_elements_text(
                    CASE 
                        WHEN final_data IS NOT NULL AND (final_data->'enriched_locations' IS NOT NULL OR final_data->'locations' IS NOT NULL) THEN 
                            COALESCE(final_data->'enriched_locations', final_data->'locations')
                        ELSE categories->'locations'
                    END
                ) as name, 
                COUNT(*) as value 
            FROM parsed_events 
            WHERE review_status = 'approved'
            GROUP BY name
            ORDER BY value DESC
            LIMIT 10;
        """)
        result = await db.execute(query)
        return result.mappings().all()

    raise HTTPException(status_code=404, detail=f"Analytics chart type '{chart_type}' not found.")


@app.post("/api/ingest-parsed-tweet", status_code=201)
async def ingest_parsed_tweet(
    payload: schemas.IngestPayload,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Endpoint for the Node.js script to post parsed tweet data.
    This saves the data to the database and updates the raw tweet status.
    """
    tweet_id = payload.tweet.id
    
    # 1. Check if the parsed event already exists
    existing_event = await db.get(models.ParsedEvent, tweet_id)
    if existing_event:
        return {"status": "skipped", "message": "Parsed event already exists."}

    # 2. Create new ParsedEvent record
    new_event = models.ParsedEvent(
        id=tweet_id,
        tweet_id=tweet_id,
        categories=payload.categories.model_dump(),
        gemini_metadata=payload.gemini_metadata.model_dump(),
        event_type=payload.categories.event[0] if payload.categories.event else None,
        locations=payload.categories.locations,
        people_mentioned=payload.categories.people,
        schemes_mentioned=payload.categories.schemes,
        overall_confidence=payload.gemini_metadata.confidence,
        parsed_at=datetime.datetime.utcnow()
    )
    db.add(new_event)

    # 3. Update the status of the corresponding raw_tweet
    raw_tweet = await db.get(models.RawTweet, tweet_id)
    if raw_tweet:
        raw_tweet.processing_status = 'processed'
        raw_tweet.processed_at = datetime.datetime.utcnow()
    else:
        # If raw_tweet doesn't exist, create one
        new_raw_tweet = models.RawTweet(
            tweet_id=tweet_id,
            text=payload.tweet.text,
            created_at=payload.tweet.created_at,
            processing_status='processed',
            processed_at=datetime.datetime.utcnow()
        )
        db.add(new_raw_tweet)

    await db.commit()
    
    return {"status": "success", "message": f"Data for tweet {tweet_id} ingested."}


@app.post("/api/vector/trigger-batch-indexing")
async def trigger_vector_indexing(
    payload: schemas.VectorIndexTriggerPayload,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Triggers FAISS vector indexing for a batch of tweets.
    """
    # Lazy import
    from .vector_store import get_vector_store
    
    tweet_ids = payload.tweetIds
    if not tweet_ids:
        return {"status": "skipped", "message": "No tweet IDs provided."}

    # Fetch the text for the given tweet IDs from the database
    query = select(models.RawTweet.tweet_id, models.RawTweet.text).where(models.RawTweet.tweet_id.in_(tweet_ids))
    result = await db.execute(query)
    tweets_to_index = result.mappings().all()

    if not tweets_to_index:
        return {"status": "skipped", "message": "No matching tweets found in DB for indexing."}
        
    documents = [{"tweet_id": t["tweet_id"], "text": t["text"]} for t in tweets_to_index]
    
    # Add documents to the vector store
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    
    return {"status": "success", "service": "faiss", "message": f"Indexing triggered for {len(documents)} items."}


@app.post("/api/cognitive/correct", response_model=schemas.CorrectionResponse)
async def trigger_correction(
    payload: schemas.CorrectionRequest,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Triggers the Cognitive Reasoning Engine to analyze a correction.
    """
    engine = getattr(app.state, "cognitive_engine", None)
    if not engine:
        raise HTTPException(status_code=503, detail="Cognitive Engine is not initialized.")

    import asyncio
    from functools import partial
    
    # Run synchronous engine in threadpool
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None, 
            partial(
                engine.process_correction, 
                payload.tweet_id, 
                payload.text, 
                payload.old_data, 
                payload.correction
            )
        )
    except Exception as e:
        print(f"Error running Cognitive Engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "success" if "error" not in result else "error",
        "log_id": result.get("id"),
        "decision": result.get("decision"),
        "details": result.get("details")
    }

@app.post("/api/events/{tweet_id}/approve")
async def approve_event(
    tweet_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Marks an event as approved.
    """
    event = await db.get(models.ParsedEvent, tweet_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    event.review_status = "approved"
    event.needs_review = False
    event.reviewed_at = datetime.datetime.utcnow()
    event.reviewed_by = user.username
    
    await db.commit()
    
    return {"status": "success", "message": f"Event {tweet_id} approved"}

@app.put("/api/events/{tweet_id}")
async def update_event(
    tweet_id: str,
    payload: schemas.EventUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Updates an event's parsed data.
    """
    event = await db.get(models.ParsedEvent, tweet_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    data = payload.parsed_data
    
    # Update top-level fields
    if "event_type" in data:
        event.event_type = data["event_type"]
    
    if "location" in data and isinstance(data["location"], dict):
        loc_text = data["location"].get("canonical")
        if loc_text:
            event.locations = [loc_text]
            
    if "schemes_mentioned" in data:
        event.schemes_mentioned = data["schemes_mentioned"]
        
    if "people_mentioned" in data:
        event.people_mentioned = data["people_mentioned"]
        
    # Update categories JSONB to reflect changes
    if event.categories:
        cats = dict(event.categories)
    else:
        cats = {}
        
    if "event_type" in data:
        cats["event"] = [data["event_type"]]
    if "location" in data and isinstance(data["location"], dict):
        cats["locations"] = [data["location"].get("canonical")]
    if "schemes_mentioned" in data:
        cats["schemes"] = data["schemes_mentioned"]
    if "people_mentioned" in data:
        cats["people"] = data["people_mentioned"]
        
    event.categories = cats
    
    # Mark as edited
    event.review_status = "edited"
    event.reviewed_at = datetime.datetime.utcnow()
    event.reviewed_by = user.username
    
    await db.commit()
    
    return {"status": "success", "message": f"Event {tweet_id} updated"}


@app.post("/api/search", response_model=list[schemas.SearchResult])
async def search_tweets(
    payload: schemas.SearchRequest,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Performs a semantic search on indexed tweets.
    """
    # Lazy import to avoid blocking backend startup
    from .vector_store import get_vector_store
    
    vector_store = get_vector_store()
    if not vector_store.index or vector_store.index.ntotal == 0:
        # Fallback or empty return if index isn't ready
        return []

    results = vector_store.search(payload.query, k=payload.k)
    
    search_results = []
    for res in results:
        metadata = res.get("metadata", {})
        search_results.append(
            schemas.SearchResult(
                tweet_id=metadata.get("tweet_id", "unknown"),
                text=metadata.get("text", ""),
                score=res.get("distance", 0.0),
                metadata=metadata
            )
        )
        
    return search_results

@app.post("/api/telemetry", status_code=201)
async def log_telemetry(
    payload: schemas.TelemetryRequest,
    db: AsyncSession = Depends(get_db_session),
    # Optional auth for telemetry? Usually open or basic auth.
    # Removing strict auth for telemetry to allow capturing login errors etc.
):
    """
    Logs telemetry events from the frontend.
    """
    # In a real system, save to a dedicated table or timeseries DB.
    # For now, just print to stdout
    print(f"TELEMETRY [{payload.type.upper()}]: {payload.name} - {payload.data}")
    return {"status": "success"}


# --- Overlay Service Endpoints ---

@app.post("/api/overlay/add")
async def add_overlay_correction(
    payload: schemas.AddOverlayRequest,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Add a human-reviewed correction overlay.

    Creates a correction record that will be applied to parsed data without
    modifying the original parser output.
    """
    from .services.overlay_service import get_overlay_service

    overlay_service = get_overlay_service()

    record = overlay_service.add_overlay(
        tweet_id=payload.tweet_id,
        field=payload.field,
        corrected_value=payload.corrected_value.value,
        reviewer_id=payload.reviewer_id,
        reviewer_name=payload.reviewer_name,
        notes=payload.notes
    )

    return {
        "status": "success",
        "overlay": record.to_dict()
    }


@app.get("/api/overlay/tweet/{tweet_id}")
async def get_tweet_overlays(
    tweet_id: str,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Get all overlay corrections for a specific tweet.
    """
    from .services.overlay_service import get_overlay_service

    overlay_service = get_overlay_service()
    overlays = overlay_service.get_overlays_for_tweet(tweet_id)

    return [overlay.to_dict() for overlay in overlays]


@app.post("/api/overlay/apply")
async def apply_overlay_corrections(
    payload: schemas.ApplyOverlayRequest,
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
) -> schemas.ApplyOverlayResponse:
    """
    Apply overlay corrections to parsed data.

    Returns the corrected data with overlays applied where available.
    """
    from .services.overlay_service import get_overlay_service

    overlay_service = get_overlay_service()
    corrected_data = overlay_service.apply_overlays(
        payload.parsed_data,
        payload.tweet_id
    )

    # Count applied overlays
    overlays = overlay_service.get_overlays_for_tweet(payload.tweet_id)
    applied_count = len([
        o for o in overlays
        if o.field in payload.parsed_data and
        (o.confidence >= 0.8 or o.source == "human_review")
    ])

    return schemas.ApplyOverlayResponse(
        status="success",
        corrected_data=corrected_data,
        applied_overlays=applied_count
    )


@app.get("/api/overlay/stats")
async def get_overlay_statistics(
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Get comprehensive statistics about stored overlay corrections.
    """
    from .services.overlay_service import get_overlay_service

    overlay_service = get_overlay_service()
    stats = overlay_service.get_overlay_stats()

    return stats


@app.delete("/api/overlay/tweet/{tweet_id}")
async def clear_tweet_overlays(
    tweet_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: models.AdminUser = Depends(get_current_user),
):
    """
    Remove all overlay corrections for a specific tweet.

    Requires admin privileges for data management operations.
    """
    if "admin" not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for overlay management"
        )

    from .services.overlay_service import get_overlay_service

    overlay_service = get_overlay_service()
    removed_count = overlay_service.clear_overlays_for_tweet(tweet_id)

    return {
        "status": "success",
        "removed_overlays": removed_count
    }


@app.get("/api/overlay/health")
async def get_overlay_health(
    db: AsyncSession = Depends(get_db_session),
    _: models.AdminUser = Depends(get_current_user),
) -> schemas.OverlayHealthResponse:
    """
    Get overlay service health and performance metrics.
    """
    from .services.overlay_service import get_overlay_service
    import time

    overlay_service = get_overlay_service()

    start_time = time.time()
    stats = overlay_service.get_overlay_stats()
    query_time = time.time() - start_time

    return schemas.OverlayHealthResponse(
        status="healthy",
        query_performance_ms=round(query_time * 1000, 2),
        total_overlays=stats["total_overlays"],
        tweets_with_overlays=stats["tweets_with_overlays"],
        service_ready=True
    )



# ============================================================================
# NLQ Endpoint - PRODUCTION FAST VERSION
# 3-Tier System: Cache → Event Object → RAG+LLM
# ============================================================================

class NLQRequest(BaseModel):
    query: str
    mode: str = "auto"  # auto | fast | detailed
    force_refresh: bool = False

@app.post("/api/nlq/ask")
async def ask_nlq_fast(
    payload: NLQRequest,
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Fast NLQ with 3-tier response system:
    1. Cache Hit: ~10-50ms (instant)
    2. Event Object Template: ~500ms-1s (structured data)
    3. RAG + LLM: ~50s+ (comprehensive, optional)
    
    Modes:
    - auto: Smart fallback (cache → event → LLM if needed)
    - fast: Only cache + event objects (no LLM)
    - detailed: Always use LLM for comprehensive analysis
    """
    from backend.services.fast_nlq_service import get_fast_nlq_service
    
    try:
        service = get_fast_nlq_service()
        
        # Determine whether to use LLM
        use_llm = (
            payload.mode == "detailed" or
            (payload.mode == "auto" and "पूरी जानकारी" in payload.query.lower())
        )
        
        response = await service.answer_query(
            query=payload.query,
            use_llm_polish=use_llm,
            force_refresh=payload.force_refresh
        )
        
        return response.dict()
        
    except Exception as e:
        print(f"NLQ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint (for backwards compatibility)
@app.post("/api/nlq/ask/legacy")
async def ask_nlq_legacy(
    payload: NLQRequest,
    _: models.AdminUser = Depends(get_current_user),
):
    """
    Legacy NLQ endpoint (old behavior).
    Always uses RAG + LLM.
    """
    import time
    import re
    from backend.cognitive.nlq_engine import get_nlq_engine
    
    start_time = time.time()
    
    try:
        engine = get_nlq_engine()
        result = engine.answer_query(payload.query)
        
        # Calculate quality score
        answer = result.get('answer', '')
        quality_score = 0
        missing_fields = []
        
        # Check for explicit dates
        if re.search(r'\d{4}|\d{1,2}\s+(जनवरी|फरवरी|मार्च|अप्रैल|मई|जून)', answer):
            quality_score += 1
        else:
            missing_fields.append('explicit_date')
        
        # Check for location
        if re.search(r'(रायपुर|बिलासपुर|नवा रायपुर)', answer, re.IGNORECASE):
            quality_score += 1
        else:
            missing_fields.append('location')
        
        # Check for person names
        if re.search(r'(मुख्यमंत्री|CM|ओपी चौधरी)', answer, re.IGNORECASE):
            quality_score += 1
        else:
            missing_fields.append('person_name')
        
        # Check for amounts/numbers
        if any(keyword in payload.query.lower() for keyword in ['कितनी राशि', 'amount', 'भर्ती']):
            if re.search(r'₹|करोड़|लाख|\d+\s*भर्तियाँ', answer):
                quality_score += 1
            else:
                missing_fields.append('amount_or_number')
        else:
            quality_score += 1
        
        # Add metadata
        result['quality_score'] = quality_score
        result['missing_fields'] = missing_fields
        result['response_time_seconds'] = round(time.time() - start_time, 2)
        result['response_mode'] = 'rag_llm_legacy'
        
        print(f"Legacy NLQ: {payload.query[:50]}... | Quality: {quality_score}/4 | Time: {result['response_time_seconds']}s")
        
        return result
        
    except Exception as e:
        print(f"NLQ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """
    Warmup the NLQ Engine (Load Gemma 3) on startup for faster first response.
    """
    print("🔥 Warming up NLQ Engine (Background Load)...")
    import asyncio
    from backend.cognitive.nlq_engine import get_nlq_engine
    
    # Run in a separate thread/task to not block startup
    # But for MLX, we might want to trigger the load.
    # We'll just initialize the engine, which triggers lazy load ONLY when used?
    # No, MLXEngine.load_model() is explicit.
    # NLQEngine init doesn't load model.
    # We need to explicitly call load_model.
    
    try:
        engine = get_nlq_engine()
        # Trigger model load in background
        asyncio.create_task(warmup_model(engine))
    except Exception as e:
        print(f"⚠️ Warmup failed: {e}")

async def warmup_model(nlq_engine):
    print("⏳ Loading Gemma 3 Model into Memory...")
    try:
        # This is a blocking call on the thread, so we should be careful.
        # But in asyncio, we can't easily offload CPU bound work without blocking loop unless using run_in_executor.
        # However, MLX load is fast-ish (IO bound).
        # Let's just call it.
        nlq_engine.llm_engine.load_model()
        print("✅ Gemma 3 Model Loaded & Ready!")
    except Exception as e:
        print(f"❌ Model load failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
