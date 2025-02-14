from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


def create_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    print("DONE CREATING TABLES")


create_tables()
