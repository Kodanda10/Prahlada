"""
Stats service for tweet statistics and counts.

Handles all database queries related to tweet statistics.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..core.logging import get_logger
from ..core.exceptions import DatabaseError
from .. import models

logger = get_logger(__name__)


class StatsService:
    """Service for retrieving tweet statistics."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the stats service.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def get_tweet_stats(self) -> Dict[str, int]:
        """
        Get summary statistics for tweets.
        
        Returns:
            Dictionary with tweet counts by status
            
        Raises:
            DatabaseError: If database query fails
        """
        try:
            # Build queries
            total_query = select(func.count(models.RawTweet.tweet_id))
            processed_query = select(func.count(models.RawTweet.tweet_id)).where(
                models.RawTweet.processing_status == 'processed'
            )
            pending_query = select(func.count(models.RawTweet.tweet_id)).where(
                models.RawTweet.processing_status == 'pending'
            )
            failed_query = select(func.count(models.RawTweet.tweet_id)).where(
                models.RawTweet.processing_status == 'failed'
            )
            
            # Execute queries
            total_result = await self.db.execute(total_query)
            processed_result = await self.db.execute(processed_query)
            pending_result = await self.db.execute(pending_query)
            failed_result = await self.db.execute(failed_query)
            
            stats = {
                "total_tweets": total_result.scalar_one(),
                "parsed_success": processed_result.scalar_one(),
                "pending": pending_result.scalar_one(),
                "errors": failed_result.scalar_one(),
            }
            
            logger.info(f"Retrieved tweet stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get tweet stats: {e}")
            raise DatabaseError(
                message="Failed to retrieve tweet statistics",
                operation="get_tweet_stats"
            )
    
    async def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get detailed processing summary including rates.
        
        Returns:
            Dictionary with processing statistics and rates
        """
        stats = await self.get_tweet_stats()
        
        total = stats["total_tweets"]
        if total > 0:
            success_rate = (stats["parsed_success"] / total) * 100
            error_rate = (stats["errors"] / total) * 100
            pending_rate = (stats["pending"] / total) * 100
        else:
            success_rate = error_rate = pending_rate = 0.0
        
        return {
            **stats,
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "pending_rate": round(pending_rate, 2),
        }
