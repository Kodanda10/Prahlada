import os
print("DEBUG: Imported os")
import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, Depends, status
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
from .vector_store import get_vector_store
print("DEBUG: Imported vector_store")
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
            # print("DEBUG: Database connected. Creating tables...")
            # await conn.run_sync(models.Base.metadata.drop_all) # Use for development reset
            # await conn.run_sync(models.Base.metadata.create_all)
            # print("DEBUG: Tables created.")
            pass
    except Exception as e:
        print(f"DEBUG: Database connection failed: {e}")
        raise e

    print("DEBUG: Database initialization complete.")
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if admin_username and admin_password:
        async with AsyncSessionLocal() as session:
            await ensure_default_admin(session, admin_username, admin_password)
    else:
        print("WARNING: ADMIN_USERNAME/ADMIN_PASSWORD not set. No default admin user provisioned.")
    
    # Initialize vector store during startup (lazy initialization)
    print("Initializing vector store...")
    try:
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
        from .cognitive.engine import CognitiveEngine
        app.state.cognitive_engine = CognitiveEngine()
        print("Cognitive Engine is ready.")
    except Exception as e:
        print(f"WARNING: Cognitive Engine initialization failed: {e}")
        app.state.cognitive_engine = None
    
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
    status: str | None = None,
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
        select(models.ParsedEvent, models.RawTweet)
        .join(models.RawTweet, models.RawTweet.tweet_id == models.ParsedEvent.tweet_id, isouter=True)
        .order_by(models.ParsedEvent.parsed_at.desc())
        .limit(3000)
    )
    if status_filter:
        query = query.where(models.RawTweet.processing_status == status_filter)

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

    def map_status(raw_status: str | None):
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
    for parsed_event, raw_tweet in rows:
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

        response.append({
            "tweet_id": parsed_event.tweet_id,
            "created_at": raw_tweet.created_at if raw_tweet and raw_tweet.created_at else parsed_event.parsed_at,
            "raw_text": raw_text,
            "clean_text": clean_text,
            "event_type": event_types,
            "location_text": location_text,
            "scheme_tags": scheme_tags,
            "people_mentioned": people,
            "word_buckets": word_buckets,
            "parsing_status": map_status(raw_tweet.processing_status if raw_tweet else None),
            "logs": log_entries or ["Loaded from parsed_events"]
        })

    return response


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
        # Note: This is an example of a raw SQL query for aggregation.
        # A more robust solution might use SQLAlchemy's aggregation functions.
        query = text("""
            SELECT 
                (jsonb_array_elements_text(categories->'event')) as name, 
                COUNT(*) as value 
            FROM parsed_events 
            WHERE categories->'event' IS NOT NULL
            GROUP BY name
            ORDER BY value DESC
            LIMIT 10;
        """)
        result = await db.execute(query)
        return result.mappings().all()
        
    if chart_type == "districts":
        query = text("""
            SELECT 
                (jsonb_array_elements_text(categories->'locations')) as name, 
                COUNT(*) as value 
            FROM parsed_events 
            WHERE categories->'locations' IS NOT NULL
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


