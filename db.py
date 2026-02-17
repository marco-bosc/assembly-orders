from sqlalchemy import create_engine

DB_BACKEND = "sqlite"  # cambia SOLO questo

DATABASES = {
    "sqlite": "sqlite:///database.db",
    "postgres": "postgresql+psycopg2://user:password@host:5432/dbname",
}

DATABASE_URL = DATABASES[DB_BACKEND]

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True
)
