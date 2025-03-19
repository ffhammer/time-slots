from datetime import timedelta
from dotenv import load_dotenv
import os

assert load_dotenv()

START_DAY = int(os.environ["STARTING_HOUR"])
END_DAY = int(os.environ["ENDING_HOUR"])
N_DAYS_AHEAD = int(os.environ["N_DAYS_AHEAD"])

MAX_TIME_SPAN = timedelta(hours=int(os.environ["MAX_VALID_HOURS"]))
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]
