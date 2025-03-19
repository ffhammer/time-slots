from datetime import datetime, timedelta
from database import get_bookings_inbetween
from config import START_DAY, END_DAY, N_DAYS_AHEAD


def get_availability():

    today = datetime.now().date()
    avail = {}
    for offset in range(N_DAYS_AHEAD):
        day = today + timedelta(days=offset)
        day_str = day.strftime("%Y-%m-%d")
        day_start = datetime(day.year, day.month, day.day, START_DAY)
        day_end = datetime(day.year, day.month, day.day, END_DAY)
        blocks = []
        current = day_start
        for res_start, res_end, user_name in get_bookings_inbetween(day_start, day_end):
            if current < res_start:
                block = {
                    "offset": int((current - day_start).total_seconds() / 60),
                    "duration": int((res_start - current).total_seconds() / 60),
                    "status": "free",
                }
                blocks.append(block)
            block = {
                "offset": int((res_start - day_start).total_seconds() / 60),
                "duration": int((res_end - res_start).total_seconds() / 60),
                "status": "reserved",
                "name": user_name,
            }
            blocks.append(block)
            current = res_end
        if current < day_end:
            block = {
                "offset": int((current - day_start).total_seconds() / 60),
                "duration": int((day_end - current).total_seconds() / 60),
                "status": "free",
            }
            blocks.append(block)
        avail[day_str] = blocks
    return avail
