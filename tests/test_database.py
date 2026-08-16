"""Tests for the database session dependency."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

import backend.database.session as session_module
from backend.database.session import get_db


def test_get_db_yields_a_usable_session() -> None:
    """get_db yields a real ORM session that can execute queries."""
    generator = get_db()
    db = next(generator)
    try:
        assert isinstance(db, Session)
        assert db.execute(text("SELECT 1")).scalar() == 1
    finally:
        generator.close()


def test_get_db_closes_session_on_generator_close() -> None:
    """The finally block closes the session when the generator is closed."""
    mock_session = Mock()
    mock_factory = Mock(return_value=mock_session)
    original = session_module.SessionLocal
    session_module.SessionLocal = mock_factory
    try:
        generator = get_db()
        yielded = next(generator)
        assert yielded is mock_session

        generator.close()
    finally:
        session_module.SessionLocal = original

    mock_session.close.assert_called_once_with()


def test_get_db_exhausts_after_close() -> None:
    """Closing the generator also runs its finally and exhausts it."""
    generator = get_db()
    next(generator)
    generator.close()
    with pytest.raises(StopIteration):
        next(generator)
