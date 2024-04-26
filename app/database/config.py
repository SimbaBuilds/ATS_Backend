from sqlalchemy import create_engine

DATABASE_URL = "postgresql://cameronhightower:Wellpleased22!@localhost:5432/automated_tutoring_service"

engine = create_engine(DATABASE_URL)
