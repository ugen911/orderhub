import os
import platform
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(), override=True)


def ping(host):
    """
    Проверяет доступность IP-адреса (или hostname).
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    response = os.system(f"ping {param} 1 {host} > nul")
    return response == 0


def get_db_config():
    """
    Определяет тип подключения на основе доступного IP.
    """
    if ping("192.168.1.88"):
        print("✅ Подключение по локальной сети")
        host = "192.168.1.88"
    elif ping("26.218.196.12"):
        print("✅ Подключение по Radmin VPN")
        host = "26.218.196.12"
    else:
        print("✅ Локальное подключение")
        host = "localhost"

    return {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "host": host,
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
    }
