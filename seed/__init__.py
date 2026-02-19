import sys
import json
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
import os

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from typing import Dict
from seed.utils.admin import create_user
from seed.utils.category import create_category

from seed.utils.helper import get_data, truncate_all_tables

datas: Dict = get_data()

def run_seed():
    db: Session = SessionLocal()
    # Truncate all tables before seeding to ensure a clean slate
    truncate_all_tables(db)
    
    # Process each dataset based on the filename and call the appropriate seeding function
    for key, value in datas.items():
        print(f"Processing dataset: {key} with {len(value)} records")
        if key == 'd01-admins':
            create_user(db, value)
            print(f"Seeded {len(value)} admins successfully.")

        if key == 'd02-categories':
            create_category(db, value)
            print(f"Seeded {len(value)} categories successfully.")
            

    db.close()


if __name__ == "__main__":
    run_seed()