# test_db.py
import pytest
from sqlalchemy.orm import Session as SQLAlchemySession

from backend.database.database import get_db


def test_get_db_returns_session():
    db_gen = get_db()
    db = next(db_gen)

    assert isinstance(db, SQLAlchemySession)

    try:
        next(db_gen)
    except StopIteration:
        pass


def test_get_db_closes_session():
    db_gen = get_db()
    db = next(db_gen)

    assert db.is_active

    with pytest.raises(StopIteration):
        next(db_gen)

    assert not db.is_active or db.close