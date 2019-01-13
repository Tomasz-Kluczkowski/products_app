import pytest

from database.database import Base, engine, init_db

from app import app


@pytest.fixture
def client():
    # This fixture accesses main database.
    # TODO: find a way to use temporary database
    Base.metadata.drop_all(engine)
    init_db()
    app.config["TESTING"] = True
    client = app.test_client()

    yield client
