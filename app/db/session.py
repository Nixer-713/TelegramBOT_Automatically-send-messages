"""Stage 1 database session helpers."""  # Module docstring indicating session management utilities
from __future__ import annotations  # Enable postponed annotations for typing flexibility

from contextlib import contextmanager  # Provide decorator to build session scope context manager
from typing import Iterator  # Type hint representing generator output of context manager

from sqlmodel import Session, SQLModel, create_engine  # Import ORM session, metadata base, and engine factory

from app.config import get_settings  # Access configuration to retrieve current DATABASE_URL value

_ENGINE = None  # Cache SQLModel engine instance for reuse across calls
_CURRENT_URL = None  # Track database URL used to build cached engine


def get_engine():  # Retrieve or build SQLModel engine respecting cached values
    """Return a SQLModel engine configured for the current database URL."""  # Docstring clarifying function behaviour

    global _ENGINE, _CURRENT_URL  # Mutate module-level cache variables when necessary
    settings = get_settings()  # Load current configuration including database URL
    if _ENGINE is None or _CURRENT_URL != settings.database_url:  # Rebuild engine when missing or URL changed
        if _ENGINE is not None:  # If existing engine present dispose connections cleanly
            _ENGINE.dispose()  # Release pooled connections prior to replacement
        _ENGINE = create_engine(settings.database_url, echo=False, pool_pre_ping=True)  # Construct new engine using SQLModel helper
        _CURRENT_URL = settings.database_url  # Record URL used to construct engine for future comparisons
    return _ENGINE  # Return cached or newly created engine to caller


def reset_engine() -> None:  # Exposed utility to force engine rebuild (mainly for tests)
    """Drop the cached engine so tests can force a rebuild."""  # Docstring documenting reset intention

    global _ENGINE, _CURRENT_URL  # Reference cache variables declared at module scope
    if _ENGINE is not None:  # If engine exists dispose resources before clearing
        _ENGINE.dispose()  # Close pooled connections to avoid locked SQLite files
    _ENGINE = None  # Clear engine reference so next get_engine call recreates one
    _CURRENT_URL = None  # Reset stored URL to ensure mismatch triggers rebuild


def init_db() -> None:  # Create tables defined in SQLModel metadata
    """Create database tables for the current metadata."""  # Docstring summarising schema initialisation

    SQLModel.metadata.create_all(get_engine())  # Use ORM metadata to create tables on configured engine


@contextmanager  # Convert generator function into context manager for session handling
def session_scope() -> Iterator[Session]:  # Provide caller with session that automatically closes/commits
    """Provide a transactional scope around a series of operations."""  # Docstring describing transactional behaviour

    with Session(get_engine()) as session:  # Open SQLModel session bound to cached engine
        yield session  # Expose session to caller, automatically closing afterwards


if __name__ == "__main__":  # pragma: no cover - CLI helper  # Allow module to act as script for initialisation
    init_db()  # Initialise database schema when run as standalone script
    print("Database initialised.")  # Display confirmation message in console
