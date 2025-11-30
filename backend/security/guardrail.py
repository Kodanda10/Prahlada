from typing import Optional
from ..core.logging import get_logger

logger = get_logger(__name__)

class Guardrail:
    """
    Security Guardrail to prevent unauthorized modifications to critical data.
    Enforces rules like "No deletion of Schemes".
    """
    
    CRITICAL_TABLES = ["schemes", "government_programs"]
    
    @staticmethod
    def validate_delete(table_name: str, record_id: Optional[str] = None) -> bool:
        """
        Check if a delete operation is allowed.
        
        Args:
            table_name: Name of the table being modified
            record_id: ID of the record being deleted (optional)
            
        Returns:
            True if allowed, False if blocked.
        """
        # Rule 1: Protect Critical Tables
        if table_name in Guardrail.CRITICAL_TABLES:
            logger.warning(f"GUARDRAIL: Blocked deletion from critical table '{table_name}'")
            return False
            
        # Rule 2: Protect "Scheme" type events (if applicable)
        # This would require fetching the record first, which might be done by the caller
        
        return True

    @staticmethod
    def validate_schema_change(operation: str, target: str) -> bool:
        """
        Prevent unauthorized schema changes (e.g., dropping tables).
        """
        if operation == "drop_table" and target in Guardrail.CRITICAL_TABLES:
             logger.critical(f"GUARDRAIL: Blocked DROP TABLE for '{target}'")
             return False
        return True
