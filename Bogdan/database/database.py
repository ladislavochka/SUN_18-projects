from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_database():
    with engine.begin() as connection:
        for table in ("books", "authors"):
            columns = [
                row[1]
                for row in connection.execute(
                    text(f"PRAGMA table_info({table})")
                )
            ]

            if columns and "image_name" not in columns:
                connection.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN image_name VARCHAR")
                )
