from app.database.local_db import local_db


def get_db():
    gen = local_db.get_db()
    session = next(gen)
    try:
        yield session
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
