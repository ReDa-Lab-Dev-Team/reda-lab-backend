from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.admin import Admin
from app.utils.hash_pw import hash_pw

def seed_admins():
    """Seed admin users into the database"""
    db: Session = SessionLocal()
    
    try:
        admins_data = [
            {
                "username": "admin1",
                "email": "admin1@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin2",
                "email": "admin2@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin3",
                "email": "admin3@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin4",
                "email": "admin4@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin5",
                "email": "admin5@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin6",
                "email": "admin6@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin7",
                "email": "admin7@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin8",
                "email": "admin8@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin9",
                "email": "admin9@gmail.com",
                "password": "1111",
            },
            {
                "username": "admin10",
                "email": "admin10@gmail.com",
                "password": "1111",
            }
        ]
        
        for admin_data in admins_data:
            # Check if admin already exists
            existing_admin = db.query(Admin).filter(
                (Admin.email == admin_data["email"]) | 
                (Admin.username == admin_data["username"])
            ).first()
            
            if existing_admin:
                print(f"Admin {admin_data['username']} already exists. Skipping...")
                continue
            
            # Hash the password
            hashed_password = hash_pw(admin_data["password"])
            
            # Create new admin
            new_admin = Admin(
                username=admin_data["username"],
                email=admin_data["email"],
                hashed_password=hashed_password,
                is_active=True
            )
            
            db.add(new_admin)
            print(f"Created admin: {admin_data['username']}")
        
        db.commit()
        print("\nAdmin seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding admins: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting admin seeding...")
    seed_admins()