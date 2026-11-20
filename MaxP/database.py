from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Нові колонки таблиці books. create_all() не змінює вже наявні таблиці,
# тож для старої books_app.db додаємо їх вручну, і дані користувачів лишаються цілими.
_NEW_BOOK_COLUMNS = {
    "genre": "VARCHAR",
    "year": "INTEGER",
    "rating": "INTEGER",
    "created_at": "DATETIME",
}


def upgrade_schema() -> None:
    inspector = inspect(engine)
    if "books" not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns("books")}
    with engine.begin() as conn:
        for name, ddl in _NEW_BOOK_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE books ADD COLUMN {name} {ddl}"))
