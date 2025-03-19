from db.database import get_db_engine, create_database_user

engine = get_db_engine()

if engine:
    create_database_user(engine, "app", "89232808797")
