"""
FastAPI Router Registration
All API routes are registered here with proper prefixes
"""

from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.notes import router as notes_router
from app.routes.folders import router as folders_router
from app.routes.tags import router as tags_router
from app.routes.attachments import router as attachments_router


# Main API Router - combines all sub-routers
router = APIRouter()

# Include all route modules with their prefixes
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(notes_router, prefix="/notes", tags=["Notes"])
router.include_router(folders_router, prefix="/folders", tags=["Folders"])
router.include_router(tags_router, prefix="/tags", tags=["Tags"])
router.include_router(attachments_router, prefix="/attachments", tags=["Attachments"])
