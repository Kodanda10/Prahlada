"""
Cognitive Interface Layer for Project Prahlada.

Standardized interface for all cognitive/AI operations.
Provides clean separation between core parser logic and AI enhancements.
"""

from typing import Dict, Any, List, Optional
from ..core.logging import get_logger
from ..core.exceptions import ExternalServiceError

logger = get_logger(__name__)


class CognitiveInterface:
    """
    Unified interface for cognitive operations.

    Provides standardized access to AI/ML capabilities while maintaining
    clear separation from core parser logic.
    """

    def __init__(self, phi_adapter: Optional['PhiAdapter'] = None):
        """
        Initialize cognitive interface.

        Args:
            phi_adapter: Phi 3.5 adapter instance (optional, will use global if None)
        """
        if phi_adapter is None:
            from .phi_adapter import get_phi_adapter
            phi_adapter = get_phi_adapter()
        self.phi_adapter = phi_adapter

    async def suggest_parser_enhancements(
        self,
        tweet_id: str,
        raw_tweet: str,
        current_parsed: Dict[str, Any]
    ) -> 'PhiSuggestions':
        """
        Suggest enhancements to parsed tweet data.

        This is the primary cognitive interface for parser improvements.
        All suggestions are advisory and require human review.

        Args:
            tweet_id: Tweet identifier
            raw_tweet: Original tweet text
            current_parsed: Current parser output

        Returns:
            PhiSuggestions object with structured enhancement suggestions
        """
        logger.debug("Requesting parser enhancement suggestions", extra={"tweet_id": tweet_id})

        try:
            suggestions = self.phi_adapter.suggest_parser_corrections(
                tweet_id=tweet_id,
                raw_tweet=raw_tweet,
                current_parsed=current_parsed
            )

            logger.info("Parser enhancement suggestions generated", extra={
                "tweet_id": tweet_id,
                "suggestions_count": len(suggestions.event_type_suggestions) +
                                   len(suggestions.location_candidates) +
                                   len(suggestions.scheme_suggestions),
                "confidence": suggestions.confidence_score
            })

            return suggestions

        except ExternalServiceError:
            # Re-raise ExternalServiceError as-is
            raise
        except Exception as e:
            logger.error("Cognitive enhancement failed", extra={
                "tweet_id": tweet_id,
                "error": str(e)
            })
            raise ExternalServiceError(
                service="cognitive_interface",
                reason=f"Enhancement suggestion failed: {str(e)}"
            )

    async def validate_location_inference(
        self,
        tweet_id: str,
        raw_tweet: str,
        candidates: List[str]
    ) -> 'PhiSuggestions':
        """
        Validate and enhance location inferences.

        Args:
            tweet_id: Tweet identifier
            raw_tweet: Original tweet text
            candidates: Potential location strings from parser

        Returns:
            PhiSuggestions with location validation and disambiguation
        """
        logger.debug("Requesting location validation", extra={
            "tweet_id": tweet_id,
            "candidates_count": len(candidates)
        })

        try:
            suggestions = self.phi_adapter.suggest_geo_disambiguation(
                tweet_id=tweet_id,
                raw_tweet=raw_tweet,
                location_candidates=candidates
            )

            logger.info("Location validation completed", extra={
                "tweet_id": tweet_id,
                "validated_locations": len(suggestions.location_candidates),
                "confidence": suggestions.confidence_score
            })

            return suggestions

        except ExternalServiceError:
            raise
        except Exception as e:
            logger.error("Location validation failed", extra={
                "tweet_id": tweet_id,
                "error": str(e)
            })
            raise ExternalServiceError(
                service="cognitive_interface",
                reason=f"Location validation failed: {str(e)}"
            )

    async def rank_event_candidates(
        self,
        tweet_id: str,
        raw_tweet: str,
        candidates: List[str]
    ) -> 'PhiSuggestions':
        """
        Rank and validate event type candidates.

        Args:
            tweet_id: Tweet identifier
            raw_tweet: Original tweet text
            candidates: Event type candidates from parser

        Returns:
            PhiSuggestions with ranked event type suggestions
        """
        logger.debug("Requesting event candidate ranking", extra={
            "tweet_id": tweet_id,
            "candidates_count": len(candidates)
        })

        try:
            suggestions = self.phi_adapter.rank_event_type_candidates(
                tweet_id=tweet_id,
                raw_tweet=raw_tweet,
                candidates=candidates
            )

            logger.info("Event ranking completed", extra={
                "tweet_id": tweet_id,
                "ranked_events": len(suggestions.event_type_suggestions),
                "confidence": suggestions.confidence_score
            })

            return suggestions

        except ExternalServiceError:
            raise
        except Exception as e:
            logger.error("Event ranking failed", extra={
                "tweet_id": tweet_id,
                "error": str(e)
            })
            raise ExternalServiceError(
                service="cognitive_interface",
                reason=f"Event ranking failed: {str(e)}"
            )

    def check_cognitive_readiness(self) -> Dict[str, Any]:
        """
        Check readiness of cognitive services.

        Returns:
            Dict with readiness status of cognitive components
        """
        phi_ready = self.phi_adapter.check_health() if self.phi_adapter.enabled else False

        status = {
            "cognitive_services_ready": phi_ready,
            "phi_3_5_enabled": self.phi_adapter.enabled,
            "phi_3_5_available": phi_ready,
            "cognitive_capabilities": []
        }

        if phi_ready:
            status["cognitive_capabilities"] = [
                "parser_enhancement_suggestions",
                "location_disambiguation",
                "event_type_ranking",
                "scheme_detection_assistance"
            ]

        logger.debug("Cognitive readiness checked", extra=status)
        return status

    def get_cognitive_status(self) -> Dict[str, Any]:
        """
        Get detailed status of cognitive components.

        Returns:
            Detailed status information
        """
        return {
            "phi_3_5": {
                "enabled": self.phi_adapter.enabled,
                "available": self.phi_adapter.check_health() if self.phi_adapter.enabled else False,
                "model": getattr(self.phi_adapter.client, 'model', None) if self.phi_adapter.client else None
            },
            "capabilities": self.check_cognitive_readiness()["cognitive_capabilities"]
        }


# Global instance
_cognitive_interface = None

def get_cognitive_interface() -> CognitiveInterface:
    """
    Get or create the global cognitive interface instance.

    Uses lazy initialization.
    """
    global _cognitive_interface
    if _cognitive_interface is None:
        _cognitive_interface = CognitiveInterface()
    return _cognitive_interface

def configure_cognitive_interface(
    phi_enabled: bool = False,
    phi_base_url: str = "http://localhost:11434",
    phi_model: str = "phi3.5"
) -> None:
    """
    Configure the global cognitive interface.

    Call during application startup.
    """
    from .phi_adapter import set_phi_adapter_config

    # Configure Phi adapter
    set_phi_adapter_config(
        enabled=phi_enabled,
        base_url=phi_base_url,
        model=phi_model
    )

    # Create interface with configured adapter
    global _cognitive_interface
    from .phi_adapter import get_phi_adapter
    _cognitive_interface = CognitiveInterface(phi_adapter=get_phi_adapter())

    logger.info("Cognitive interface configured", extra={
        "phi_enabled": phi_enabled,
        "phi_model": phi_model
    })