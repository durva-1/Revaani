from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from database import get_users_collection

# Initialize FastAPI app
app = FastAPI(
    title="ReVaani API",
    description="Gujarati Accent-Aware Voice Assistant",
    version="1.0.0"
)

# Enable CORS (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== SCHEMAS =====================
# These define what data the API accepts

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str
    region: str  # e.g., "Ahmedabad", "Surat"

class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response (without password)"""
    user_id: str
    email: str
    full_name: str
    region: str
    created_at: str

# ===================== UTILITY FUNCTIONS =====================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id() -> str:
    """Generate unique user ID"""
    return secrets.token_hex(12)

def generate_token() -> str:
    """Generate simple authentication token"""
    return secrets.token_urlsafe(32)

# ===================== API ROUTES =====================

@app.get("/health")
def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "message": "ReVaani API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/auth/register", response_model=UserResponse)
def register(request: RegisterRequest):
    """
    Register a new user.
    
    Takes: email, password, full_name, region
    Returns: user_id, email, full_name, region, created_at
    """
    
    users_collection = get_users_collection()
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Create new user
    user_id = generate_user_id()
    user_data = {
        "user_id": user_id,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "full_name": request.full_name,
        "region": request.region,
        "created_at": datetime.now().isoformat(),
        "is_admin": False,
        "is_active": True
    }
    
    # Save to MongoDB
    result = users_collection.insert_one(user_data)
    
    # Return user response (without password)
    return {
        "user_id": user_id,
        "email": request.email,
        "full_name": request.full_name,
        "region": request.region,
        "created_at": user_data["created_at"]
    }

@app.post("/auth/login")
def login(request: LoginRequest):
    """
    Login user and return token.
    
    Takes: email, password
    Returns: user_id, token, email
    """
    
    users_collection = get_users_collection()
    
    # Find user
    user = users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Check password
    password_hash = hash_password(request.password)
    if password_hash != user["password_hash"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Generate token
    token = generate_token()
    
    # Return login response
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "token": token,
        "message": "Login successful"
    }

@app.get("/user/profile/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: str):
    """
    Get user profile by user_id.
    
    Takes: user_id (from URL)
    Returns: user data without password
    """
    
    users_collection = get_users_collection()
    
    # Find user
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Return user response
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "region": user["region"],
        "created_at": user["created_at"]
    }

# ===================== RUN SERVER =====================
# This part runs the server when you execute: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)