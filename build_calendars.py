import os
import pandas as pd
from ics import Calendar, Event
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

csv_url = os.getenv('CSV_URL', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRwoBRBFI-z4haeZv0WMruMzGmebRVPIa-pYOzbMVBX9Si9iQa8VMBzkoYjWt8VRck6OB9853xSSPzM/pub?gid=0&single=true&output=csv')

logger.info("Loading CSV...")
try:
    df = pd.read_csv(csv_url)
    logger.info(f"CSV loaded with {len(df)} rows.")
    logger.info(f"First 5 rows: {df.head()}")
except Exception as e:
    logger.error(f"Failed to load CSV: {e}")
    exit(1)

Path('public').mkdir(parents=True, exist_ok=True)

cal = Calendar()

# Add a test event
event = Event()
event.name = "Test Event"
event.begin = '2025-09-29 09:00:00+10:00'
event.end = '2025-09-29 10:00:00+10:00'
cal.events.add(event)

try:
    with open('public/test.ics', 'w') as f:
        f.write(cal.serialize())
    logger.info("Build complete.")
except Exception as e:
    logger.error(f"Failed to write ICS file: {e}")
    exit(1)
