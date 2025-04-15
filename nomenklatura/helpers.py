from datetime import datetime
from dateutil.relativedelta import relativedelta


def generate_last_months(n=36):
    """
    Возвращает список последних n месяцев в формате YYYY-MM,
    начиная с текущего месяца и назад.
    """
    now = datetime.now()
    start = now - relativedelta(months=n - 1)
    return [
        f"{start.year + (start.month + i - 1) // 12}-{(start.month + i - 1) % 12 + 1:02}"
        for i in range(n)
    ]
