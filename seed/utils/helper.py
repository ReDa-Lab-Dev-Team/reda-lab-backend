import json
from typing import Dict
import os
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import Base

def get_name_file(file):
    name_file = file.split('.')[0]
    return name_file
        
def get_data():
    current_dictionary = Path(__file__).parent.parent
    dataset_path = os.path.join(current_dictionary, 'data')
    filenames = sorted(os.listdir(dataset_path))
    """
        when create new data in json file , make sure to name json file in sorting order , because the filename is read order,
        for example: d01-admins.json, d02-categories.json, etc.
    """

    print(f"Found {len(filenames)} dataset files: {filenames}")

    # get name of file
    filenames = [get_name_file(file) for file in filenames]

    # read data from file and seperate data by file name
    datas: Dict = {}

    for file in filenames:
        with open(os.path.join(dataset_path, file + '.json'), 'r') as f:
            datas[file] = json.load(f)
            
    return datas
            
def truncate_all_tables(db: Session):
    table_names = [table.name for table in Base.metadata.sorted_tables]
    tables = ", ".join(table_names)
    db.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;"))
    db.commit()
        
    