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

# Process all rows into events
count = 0
for idx, row in df.iterrows():
    try:
        event = Event()
        event.name = str(row.get('Title', 'Untitled'))
        event.begin = pd.to_datetime(row.get('Start Date', '2025-09-29') + ' ' + str(row.get('Start Time', '09:00:00'))).isoformat()
        event.end = pd.to_datetime(row.get('End Date', '2025-09-29') + ' ' + str(row.get('End Time', '10:00:00'))).isoformat()
        cal.events.add(event)
        count += 1
    except Exception as e:
        logger.warning(f"Skipped row {idx} due to error: {e}")
        continue

logger.info(f"Processed {count} events.")

try:
    with open('public/test.ics', 'w') as f:
        f.write(cal.serialize())
    logger.info("Build complete.")
except Exception as e:
    logger.error(f"Failed to write ICS file: {e}")
    exit(1)

# Generate a basic index.html
with open('public/index.html', 'w') as f:
    f.write("<h1>Calendar Test</h1><p><a href='test.ics'>Download ICS</a></p>")
