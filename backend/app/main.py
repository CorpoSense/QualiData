import os
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from app.config import get_settings
from app.routers import (
    users,
    agents,
    ai,
    ai_operations,
    assistant,
    auth,
    batch_ops,
    cell_ops,
    charts,
    comparison,
    datasets,
    datetime_ops,
    documents,
    health,
    missing_values,
    notifications,
    operations,
    operations_extra,
    pivot,
    profiling,
    projects,
    rate_limit,
    search_engines,
    structural_ops,
    undo_redo,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown."""
    # Startup: Run database migrations
    await run_migrations()
    # Startup: Create admin user if configured
    await create_admin_user()
    yield
    # Shutdown: cleanup if needed
    pass


async def run_migrations():
    """Run Alembic migrations on startup.

    Delegates to the shared migration runner in app.db.migrate,
    which handles async engine creation and URL conversion.
    Migrations are idempotent — safe to re-run on every startup.

    For manual CLI usage: `alembic upgrade head`
    For new migrations: `alembic revision --autogenerate -m "description"`
    """
    try:
        from app.db.migrate import run_async_migrations
        await run_async_migrations()
        logger.info("Database migrations applied")
    except Exception as e:
        logger.error(f"Database migration failed: {e}", exc_info=True)



async def create_admin_user():
    """Create admin user on startup if configured."""
    from sqlalchemy import select
    from app.db.database import get_async_session_maker
    from app.db.models import User
    
    # Check if admin env vars are set
    admin_email = os.environ.get("ADMIN_USER", "").strip()
    admin_password = os.environ.get("ADMIN_PASSWORD", "").strip()
    
    if not admin_email or not admin_password:
        logger.warning(
            "ADMIN_USER or ADMIN_PASSWORD not set. "
            "First registered user will become admin."
        )
        return
    
    try:
        async_session = get_async_session_maker()
        async with async_session() as session:
            # Check if admin already exists
            result = await session.execute(
                select(User).where(User.email == admin_email)
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                logger.info(f"Admin user already exists: {admin_email}")
                return
            
            # Check if any users exist
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            # Create admin user - use passlib directly
            import hashlib
            # Use sha256 as fallback if bcrypt fails
            try:
                password_hash = pwd_context.hash(admin_password)
            except Exception:
                # Fallback: use simple hash if bcrypt fails
                password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
            admin_user = User(
                email=admin_email,
                password_hash=password_hash,
                full_name="Admin",
                role=UserRole("admin"),
            )
            
            session.add(admin_user)
            await session.commit()
            logger.info(f"Admin user created: {admin_email}")
            
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-guided data cleaning API",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
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
    app.include_router(users.router, prefix="/api")
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
    app.include_router(pivot.router, prefix="/api")
    app.include_router(profiling.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")
    app.include_router(comparison.router, prefix="/api")
    app.include_router(assistant.router, prefix="/api")
    app.include_router(rate_limit.router, prefix="/api")
    app.include_router(cell_ops.router, prefix="/api")
    app.include_router(search_engines.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(charts.router, prefix="/api")

    # Serve Vue static files if available (for production)
    # Check multiple locations for frontend build
    possible_paths = [
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "frontend"
        ),  # Local dev
        "/app/frontend",  # Docker production
        "/app/backend/frontend",  # Alternative Docker path
    ]

    frontend_path = None
    for path in possible_paths:
        import sys

        print(
            f"DEBUG: Checking path: {path}, exists: {os.path.isdir(path)}",
            file=sys.stderr,
        )
        if os.path.isdir(path):
            frontend_path = path
            break

    if frontend_path:
        import sys

        index_path = os.path.join(frontend_path, "index.html")
        print(
            f"DEBUG: Frontend found at: {frontend_path}, index exists: {os.path.isfile(index_path)}",
            file=sys.stderr,
        )

    if frontend_path and os.path.isfile(os.path.join(frontend_path, "index.html")):
        # Note: Not mounting /static to avoid conflicts
        # Static files will be served via the catchall route

        @app.get("/")
        async def serve_frontend():
            import sys

            print(f"DEBUG: Serving root path from {frontend_path}", file=sys.stderr)
            return FileResponse(os.path.join(frontend_path, "index.html"))

        @app.get("/{path:path}")
        async def serve_frontend_catchall(path: str):
            import sys

            print(f"DEBUG: Catchall serving path: {path}", file=sys.stderr)
            # Check if it's an API request
            if path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")
            # Try to serve static file first
            static_file = os.path.join(frontend_path, path)
            if os.path.isfile(static_file):
                return FileResponse(static_file)
            # Serve index.html for SPA routing
            return FileResponse(os.path.join(frontend_path, "index.html"))

    return app


app = create_app()
