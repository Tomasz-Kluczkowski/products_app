import pytest

from database.database import Base, engine, init_db


@pytest.fixture
def recreate_database():
    Base.metadata.drop_all(engine)
    init_db()
