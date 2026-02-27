from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health, ai, auth, projects, datasets, operations, operations_extra, agents, missing_values, undo_redo, datetime_ops, structural_ops, ai_operations, batch_ops

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-guided data cleaning API",
        version="0.1.0",
        debug=settings.debug,
    )
    
    # CORS middleware for Vue frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api")
    app.include_router(ai.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(projects.router, prefix="/api")
    app.include_router(datasets.router, prefix="/api")
    app.include_router(operations.router, prefix="/api")
    app.include_router(operations_extra.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(missing_values.router, prefix="/api")
    app.include_router(undo_redo.router, prefix="/api")
    app.include_router(datetime_ops.router, prefix="/api")
    app.include_router(structural_ops.router, prefix="/api")
    app.include_router(ai_operations.router, prefix="/api")
    app.include_router(batch_ops.router, prefix="/api")
    
    return app


app = create_app()
