from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import get_settings
from app.routers import (
    agents,
    ai,
    ai_operations,
    assistant,
    auth,
    batch_ops,
    cell_ops,
    comparison,
    datasets,
    datetime_ops,
    health,
    missing_values,
    notifications,
    operations,
    operations_extra,
    profiling,
    projects,
    rate_limit,
    structural_ops,
    undo_redo,
)

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
    app.include_router(profiling.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")
    app.include_router(comparison.router, prefix="/api")
    app.include_router(assistant.router, prefix="/api")
    app.include_router(rate_limit.router, prefix="/api")
    app.include_router(cell_ops.router, prefix="/api")

    # Serve Vue static files if available (for production)
    # Check multiple locations for frontend build
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"),  # Local dev
        "/app/frontend",  # Docker production
    ]
    
    frontend_path = None
    for path in possible_paths:
        if os.path.isdir(path):
            frontend_path = path
            break
    
    if frontend_path and os.path.isfile(os.path.join(frontend_path, "index.html")):
        app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="static")
        
        @app.get("/")
        async def serve_frontend():
            return FileResponse(os.path.join(frontend_path, "index.html"))
        
        @app.get("/{path:path}")
        async def serve_frontend_catchall(path: str):
            # Check if it's an API request
            if path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")
            # Serve index.html for SPA routing
            return FileResponse(os.path.join(frontend_path, "index.html"))

    return app


app = create_app()
