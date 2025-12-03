#!/bin/bash
# Production-Grade Self-Healing Enrichment Runner
# 
# Features:
# - Auto-restart on failure
# - Checkpoint-based resume (uses existing checkpoint system)
# - Background execution
# - Progress monitoring
# - Graceful shutdown
# - Full logging

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
ENRICH_SCRIPT="$PROJECT_DIR/scripts/enrich_semantic.py"
LOG_FILE="$PROJECT_DIR/data/enrichment_runner.log"
PID_FILE="$PROJECT_DIR/data/enrichment_runner.pid"
STATUS_FILE="$PROJECT_DIR/data/enrichment_status.json"

# Configuration
MAX_RETRIES=10
RETRY_DELAY=60  # Wait 60s before retry
BATCH_SIZE=10
TIMEOUT=300  # 5 minutes per tweet

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

update_status() {
    cat > "$STATUS_FILE" <<EOF
{
  "status": "$1",
  "attempt": $2,
  "total_attempts": $MAX_RETRIES,
  "last_update": "$(date -Iseconds)",
  "pid": $$
}
EOF
}

cleanup() {
    log "Cleanup: Removing PID file"
    rm -f "$PID_FILE"
    update_status "stopped" 0
}

trap cleanup EXIT INT TERM

check_if_running() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            log_error "Enrichment already running with PID $OLD_PID"
            echo "To monitor: tail -f $LOG_FILE"
            echo "To stop: kill $OLD_PID"
            exit 1
        else
            log_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
}

run_enrichment() {
    local attempt=$1
    
    log "Starting enrichment (attempt $attempt/$MAX_RETRIES)"
    update_status "running" "$attempt"
    
    # Export PHI_ENABLED for the subprocess
    export PHI_ENABLED=true
    
    # Run enrichment with resume flag (uses checkpoint automatically)
    if "$VENV_PYTHON" "$ENRICH_SCRIPT" \
        --batch-size "$BATCH_SIZE" \
        --timeout "$TIMEOUT" \
        --resume \
        2>&1 | tee -a "$LOG_FILE"; then
        
        log_success "Enrichment completed successfully!"
        update_status "completed" "$attempt"
        return 0
    else
        local exit_code=$?
        log_error "Enrichment failed with exit code $exit_code"
        update_status "failed" "$attempt"
        return $exit_code
    fi
}

# Main execution
main() {
    log "========================================="
    log "Phase 2: Production Enrichment Runner"
    log "========================================="
    log "Configuration:"
    log "  - Batch size: $BATCH_SIZE"
    log "  - Timeout: ${TIMEOUT}s per tweet"
    log "  - Max retries: $MAX_RETRIES"
    log "  - Retry delay: ${RETRY_DELAY}s"
    log "  - Log file: $LOG_FILE"
    log "  - PID file: $PID_FILE"
    log "========================================="
    
    # Check if already running
    check_if_running
    
    # Save PID
    echo $$ > "$PID_FILE"
    log "Runner PID: $$"
    
    # Self-healing loop with auto-restart
    for attempt in $(seq 1 $MAX_RETRIES); do
        log "Attempt $attempt of $MAX_RETRIES"
        
        if run_enrichment "$attempt"; then
            log_success "All tweets enriched successfully!"
            cleanup
            exit 0
        else
            if [ $attempt -lt $MAX_RETRIES ]; then
                log_warning "Enrichment failed. Auto-restarting in ${RETRY_DELAY}s..."
                sleep "$RETRY_DELAY"
            else
                log_error "Max retries ($MAX_RETRIES) reached. Giving up."
                update_status "failed_max_retries" "$attempt"
                exit 1
            fi
        fi
    done
}

# Run in background if requested
if [ "$1" = "background" ] || [ "$1" = "bg" ]; then
    log "Starting in background mode..."
    nohup bash "$0" "foreground" >> "$LOG_FILE" 2>&1 &
    BG_PID=$!
    echo $BG_PID > "$PID_FILE"
    log_success "Started in background with PID $BG_PID"
    echo ""
    echo "Enrichment started in background!"
    echo "  PID: $BG_PID"
    echo "  Monitor: tail -f $LOG_FILE"
    echo "  Status:  cat $STATUS_FILE | python3 -m json.tool"
    echo "  Stop:    kill $BG_PID"
    echo ""
else
    # Run in foreground
    main
fi
