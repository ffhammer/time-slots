# config.py
import os
from datetime import timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

assert load_dotenv()

START_DAY = int(os.environ["STARTING_HOUR"])
END_DAY = int(os.environ["ENDING_HOUR"])
N_DAYS_AHEAD = int(os.environ["N_DAYS_AHEAD"])

MAX_TIME_SPAN = timedelta(hours=int(os.environ["MAX_VALID_HOURS"]))
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]

TIME_ZONE = ZoneInfo(os.environ["TIME_ZONE"])
LOG_LEVEL = os.environ["LOG_LEVEL"]
LOG_FILE = os.environ["LOG_FILE"]
