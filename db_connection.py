from sqlalchemy import create_engine
from orderhub.db_config import get_db_config


def get_db_engine():
    db_config = get_db_config()

    connection_string = (
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )

    engine = create_engine(connection_string)
    return engine
