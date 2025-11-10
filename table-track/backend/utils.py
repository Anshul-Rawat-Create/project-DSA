# utils.py
from datetime import datetime

def is_premium_time_slot(time_str: str) -> bool:
    """
    Premium slot: 19:00 to 22:00 (7 PM to 10 PM)
    """
    try:
        hour = int(time_str.split(':')[0])
        return 19 <= hour <= 21  # inclusive
    except:
        return False

def current_timestamp() -> int:
    return int(datetime.now().timestamp())