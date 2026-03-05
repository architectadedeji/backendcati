"""System configuration API router."""
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


def load_form_schema() -> dict:
    """Load form schema from file."""
    try:
        # Try to load from public folder first
        schema_path = Path(__file__).parent.parent.parent.parent / "streamcati-frontend" / "public" / "form_schema_with_nav.json"
        
        if not schema_path.exists():
            logger.warning(f"Form schema not found at {schema_path}")
            raise FileNotFoundError(f"Form schema not found at {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Validate schema structure
        if not isinstance(schema, dict):
            raise ValueError("Form schema must be a JSON object")
        
        if "pages" not in schema or not isinstance(schema.get("pages"), list):
            raise ValueError("Form schema must have a 'pages' array")
        
        logger.debug(f"Form schema loaded successfully: {schema.get('title', 'Unknown')} with {len(schema['pages'])} pages")
        return schema
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in form schema: {e}")
        raise ValueError(f"Invalid JSON in form schema: {e}")
    except Exception as e:
        logger.error(f"Failed to load form schema: {e}")
        raise


@router.get("/system/", response_model=dict)
async def get_system_config(
    current_user: User = Depends(get_current_user),
):
    """Get system configuration."""
    return {
        "api_version": "1.0.0",
        "environment": settings.environment,
        "testing_mode": settings.testing_mode,
        "testing_interval_minutes": settings.testing_interval_minutes,
        "production_interval_months": settings.production_interval_months,
        "cors_origins": settings.CORS_ORIGINS_LIST,
        "features": {
            "authentication": True,
            "contacts_management": True,
            "interview_tracking": True,
            "analytics": True,
        },
    }


@router.get("/form-schema/", response_model=dict)
async def get_form_schema(
    current_user: User = Depends(get_current_user),
):
    """Get interview form schema."""
    try:
        schema = load_form_schema()
        return schema
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Form schema error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load form schema: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error loading form schema: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load form schema"
        )

