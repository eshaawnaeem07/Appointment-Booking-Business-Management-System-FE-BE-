import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)


# Days of week constants
DAYS_LIST = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

DAY_MAP = {day: i for i, day in enumerate(DAYS_LIST)}

# Email constants
FROM_EMAIL = os.getenv("FROM_EMAIL", "eshaanaeem07@gmail.com").strip().strip('"').strip("'")
