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

# Process all rows into events with detailed logging and robust time handling
count = 0
for idx, row in df.iterrows():
    try:
        event = Event()
        event.name = str(row.get('Title', f'Event {idx}'))
        
        # Handle dates and times with fallback
        start_date = str(row.get('Start Date', '2025-09-29'))
        start_time = str(row.get('Start Time', '')).strip() or '09:00:00'
        end_date = str(row.get('End Date', start_date))
        end_time = str(row.get('End Time', '')).strip() or '10:00:00'

        # Parse with dayfirst=True for DD/MM/YYYY
        try:
            event.begin = pd.to_datetime(f"{start_date} {start_time}", dayfirst=True, errors='coerce').isoformat()
            if pd.isna(event.begin):
                raise ValueError("Invalid start datetime")
        except ValueError as ve:
            logger.warning(f"Skipping row {idx} (start): {ve} - Start={start_date} {start_time}")
            continue

        try:
            event.end = pd.to_datetime(f"{end_date} {end_time}", dayfirst=True, errors='coerce').isoformat()
            if pd.isna(event.end):
                raise ValueError("Invalid end datetime")
        except ValueError as ve:
            logger.warning(f"Skipping row {idx} (end): {ve} - End={end_date} {end_time}")
            continue

        if event.end <= event.begin:
            event.end = pd.to_datetime(event.begin).replace(hour=int(event.end.split('T')[1][:2]) + 1).isoformat()

        cal.events.add(event)
        count += 1
        logger.info(f"Added event {count}: {event.name} from {event.begin} to {event.end}")
    except Exception as e:
        logger.error(f"Error processing row {idx}: {e}")
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
