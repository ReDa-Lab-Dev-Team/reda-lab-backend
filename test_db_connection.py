from app.config.database import engine, settings
from sqlalchemy import text

print("=== Database Connection Test ===")
print(f"Database URL: {settings.database_url}")
print()

try:
    # Test connection
    with engine.connect() as connection:
        # Get PostgreSQL version
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("✅ Connection Successful!")
        print(f"PostgreSQL Version: {version}")
        print()
        
        # Get current database name
        result = connection.execute(text("SELECT current_database();"))
        db_name = result.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
except Exception as e:
    print(f"❌ Connection Failed!")
    print(f"Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check if PostgreSQL is running")
    print("2. Verify database 'lab_db' exists")
    print("3. Check username/password in .env")
    print("4. Verify port 5432 is correct")