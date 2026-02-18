import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.lab_entities import Category

def seed_categories():
    """Seed categories into the database"""
    db: Session = SessionLocal()
    
    try:
        categories_data = [
            {"name": "Artificial Intelligence"},
            {"name": "Renewable Energy"},
            {"name": "Climate Change"},
            {"name": "Data Science"},
            {"name": "Cybersecurity"},
            {"name": "Smart Agriculture"},
            {"name": "Internet of Things"},
            {"name": "Blockchain Technology"},
            {"name": "Digital Education"},
            {"name": "Environmental Sustainability"}
        ]
        
        for category_data in categories_data:
            # Check if category already exists
            existing_category = db.query(Category).filter(
                Category.name == category_data["name"]
            ).first()
            
            if existing_category:
                print(f"Category '{category_data['name']}' already exists. Skipping...")
                continue
            
            # Create new category
            new_category = Category(
                name=category_data["name"],
                description=f"Research and projects related to {category_data['name']}",
                status="active"
            )
            
            db.add(new_category)
            print(f"Created category: {category_data['name']}")
        
        db.commit()
        print("\nCategory seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding categories: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting category seeding...")
    seed_categories()