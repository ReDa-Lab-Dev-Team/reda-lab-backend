import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
import os

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from typing import Dict
from seeds.utils.admin import create_user
from seeds.utils.category import create_category
from seeds.utils.teammember import create_teammember
from seeds.utils.project import create_research_project
from seeds.utils.advisory_board import create_advisory_board_members
from seeds.utils.helper import get_data, truncate_all_tables

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
        
        if key == 'd03-teammember':
            create_teammember(db, value)
            print(f"Seeded {len(value)} team members successfully.")
            
        if key == 'd04-projects':
            create_research_project(db, value)
            print(f"Seeded {len(value)} research projects successfully.")
        if key == 'd05-advisory_board':
            create_advisory_board_members(db, value)
            print(f"Seeded {len(value)} advisory board members successfully.")

    db.close()


if __name__ == "__main__":
    run_seed()