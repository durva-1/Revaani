from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from .env
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Global database connection
_db = None

def get_database() -> Database:
    """
    Get MongoDB database connection.
    This function returns the database object so we can use it in FastAPI routes.
    
    Returns:
        Database: MongoDB database object
    """
    global _db
    
    if _db is None:
        # Create MongoDB client
        client = MongoClient(MONGODB_URL)
        # Select the database
        _db = client[DATABASE_NAME]
        print(f"✓ Connected to MongoDB database: {DATABASE_NAME}")
    
    return _db

def get_users_collection():
    """Get users collection"""
    db = get_database()
    return db["users"]

def get_conversations_collection():
    """Get conversations collection"""
    db = get_database()
    return db["conversations"]

def get_recordings_collection():
    """Get recordings collection"""
    db = get_database()
    return db["recordings"]