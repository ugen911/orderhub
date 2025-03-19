from sqlalchemy import create_engine, text
import os
import logging
from db.config import remote_db_config, server_db_config, ugkorea_inside_config  # Импорт конфигураций

# Настройка логгирования
logging.basicConfig(filename='data_upload_errors.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def get_db_engine():
    """
    Определяет, использовать ли локальную или сетевую базу данных, и возвращает SQLAlchemy engine для подключения к базе данных.
    Также выполняет тестовый запрос к базе данных для проверки подключения.
    """
    # Пути к директориям
    network_path = r'\\26.218.196.12\заказы'
    inside_ugkorea = r'\\192.168.1.88\заказы'
    local_path = r'D:\NAS\заказы'

    if os.path.exists(network_path):
        print(f"Используется сетевая база данных (путь: {network_path})")
        db_config = remote_db_config
    elif os.path.exists(inside_ugkorea):
        print(f"Пробуем подключиться из стен автоцентра (путь: {inside_ugkorea})")
        db_config = ugkorea_inside_config
    else:
        print(
            f"Сетевая папка недоступна, используется локальная база данных (путь: {local_path})"
        )
        db_config = server_db_config

    try:
        # Создание SQLAlchemy engine
        connection_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        engine = create_engine(connection_string)

        # Тестовый запрос для проверки подключения (например, версия PostgreSQL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()

        return engine
    except Exception as e:
        logging.error(f"Ошибка при подключении к базе данных: {e}")
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


def create_database_user(engine, user_name, user_password):
    """
    Создает нового пользователя в базе данных stroikin с полным доступом ко всем схемам и таблицам.
    """
    try:
        with engine.connect() as connection:
            # Создаем логин для пользователя
            connection.execute(
                text(f"CREATE USER {user_name} WITH PASSWORD :password;"),
                {"password": user_password},
            )

            # Даем права на подключение к базе данных stroikin
            connection.execute(
                text(f"GRANT CONNECT ON DATABASE stroikin TO {user_name};")
            )

            # Даем права на все схемы в базе данных
            connection.execute(text(f"GRANT USAGE ON SCHEMA public TO {user_name};"))

            # Даем права на все таблицы и последовательности в схеме public
            connection.execute(
                text(
                    f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {user_name};"
                )
            )
            connection.execute(
                text(
                    f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {user_name};"
                )
            )

            # Даем права на все таблицы и последовательности во всех схемах, кроме системных
            connection.execute(
                text(
                    f"DO $$ DECLARE r RECORD; BEGIN "
                    "FOR r IN (SELECT nspname FROM pg_catalog.pg_namespace WHERE nspname NOT IN ('pg_catalog', 'information_schema')) "
                    "LOOP "
                    "EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA %I TO %I', r.nspname, %s); "
                    "EXECUTE format('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA %I TO %I', r.nspname, %s); "
                    "END LOOP; END $$;"
                ),
                {"user_name": user_name},
            )

            print(
                f"Пользователь {user_name} успешно создан и получил права на все схемы и таблицы в базе данных stroikin."
            )

    except Exception as e:
        logging.error(f"Ошибка при создании пользователя: {e}")
        print(f"Ошибка при создании пользователя: {e}")
