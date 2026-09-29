import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from .env
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# DEBUG: Print what we loaded
print("=" * 60)
print("DEBUG: Environment Variables")
print("=" * 60)
print(f"MONGODB_URL: {MONGODB_URL}")
print(f"DATABASE_NAME: {DATABASE_NAME}")
print("=" * 60)

if not MONGODB_URL:
    print("ERROR: MONGODB_URL is empty or not found in .env file!")
    exit()

if not DATABASE_NAME:
    print("ERROR: DATABASE_NAME is empty or not found in .env file!")
    exit()

print("\nReVaani Database Initialization")
print("=" * 60)

try:
    # Connect to MongoDB
    print("\n1. Connecting to MongoDB Atlas...")
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("   ✓ Connected successfully!")
    
    # Get database
    db = client[DATABASE_NAME]
    print(f"   ✓ Using database: {DATABASE_NAME}")
    
    # Create collections
    print("\n2. Creating collections...")
    
    collections = [
        "users",
        "conversations",
        "recordings",
        "dataset_exports",
        "admin_logs",
        "analytics_events"
    ]
    
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"   ✓ Created collection: {collection_name}")
        else:
            print(f"   • Collection already exists: {collection_name}")
    
    # Create indexes for better performance
    print("\n3. Creating indexes...")
    
    # users collection indexes
    db.users.create_index("email", unique=True)
    db.users.create_index("user_id", unique=True)
    print("   ✓ Created indexes for users collection")
    
    # conversations collection indexes
    db.conversations.create_index("user_id")
    db.conversations.create_index("conversation_id", unique=True)
    print("   ✓ Created indexes for conversations collection")
    
    # recordings collection indexes
    db.recordings.create_index("user_id")
    db.recordings.create_index("recording_id", unique=True)
    print("   ✓ Created indexes for recordings collection")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Database Initialization Complete!")
    print("=" * 60)
    print(f"Database Name: {DATABASE_NAME}")
    print(f"Collections created: {len(collections)}")
    print("=" * 60)
    
except pymongo.errors.ServerSelectionTimeoutError:
    print("\n✗ ERROR: Could not connect to MongoDB Atlas!")
    print("   • Check your MONGODB_URL in .env file")
    print("   • Make sure your IP is whitelisted in MongoDB Atlas")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    if 'client' in locals():
        client.close()