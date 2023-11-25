from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.conf.config import settings


user = settings.postgres_user
password = settings.postgres_password
db_name = settings.postgres_name
domain = settings.postgres_domain
port = settings.postgres_port


engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db_name}")


def get_db():
    db = Session(engine)
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()
