from db import SessionLocal
from contextlib import contextmanager

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# placeholder de autorización (por ahora libre)
def current_admin_or_self():
    return True
