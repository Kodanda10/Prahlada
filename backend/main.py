import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from contextlib import asynccontextmanager
import datetime

from . import models, schemas
from .database import engine, get_db_session, AsyncSessionLocal
from .vector_store import get_vector_store
from .auth import authenticate_user, create_access_token, get_current_user, ensure_default_admin

# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    # On startup:
    print("Application startup...")
    # Initialize database tables (if they don't exist)
    async with engine.begin() as conn:
        # await conn.run_sync(models.Base.metadata.drop_all) # Use for development reset
        await conn.run_sync(models.Base.metadata.create_all)

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
    print("Application shutdown...")
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
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

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
        .limit(100)
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

    response: list[dict] = []
    for parsed_event, raw_tweet in rows:
        categories = parsed_event.categories or {}
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
