from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import hashlib
import secrets
import os
from dotenv import load_dotenv
from database import get_users_collection, get_conversations_collection
from google.genai import types
import google.genai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI(
    title="ReVaani API",
    description="Gujarati Accent-Aware Voice Assistant",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== SCHEMAS =====================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str
    region: str

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

class ChatMessage(BaseModel):
    """Chat message request"""
    user_id: str
    conversation_id: str
    text: str
    language: str = "gujarati"

class ChatResponse(BaseModel):
    """Chat response"""
    user_message: str
    ai_response: str
    timestamp: str

# ===================== UTILITY FUNCTIONS =====================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id() -> str:
    """Generate unique user ID"""
    return secrets.token_hex(12)

def generate_token() -> str:
    """Generate authentication token"""
    return secrets.token_urlsafe(32)

def generate_conversation_id() -> str:
    """Generate unique conversation ID"""
    return secrets.token_hex(12)

def get_gemini_response(user_message: str) -> str:
    """
    Get response from Gemini API.
    For now using mock response - will integrate real Gemini later.
    """
    try:
        # Mock Gujarati response (temporary)
        mock_responses = {
            "હું કોણ છું?": "તમે એક વપરાશકર્તા છો જે ReVaani સાથે વાત કરી રહ્યા છો.",
            "hello": "નમસ્તે! હું ReVaani છું. તમે કેવા છો?",
            "default": "આ એક સરસ પ્રશ્ન છે! કૃપયા ફરીથી પ્રયાસ કરો."
        }
        
        # Return mock response
        return mock_responses.get(user_message, mock_responses["default"])
    
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# ===================== AUTHENTICATION ROUTES =====================

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
    """Register a new user"""
    
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
    users_collection.insert_one(user_data)
    
    return {
        "user_id": user_id,
        "email": request.email,
        "full_name": request.full_name,
        "region": request.region,
        "created_at": user_data["created_at"]
    }

@app.post("/auth/login")
def login(request: LoginRequest):
    """Login user and return token"""
    
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
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "token": token,
        "message": "Login successful"
    }

@app.get("/user/profile/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: str):
    """Get user profile by user_id"""
    
    users_collection = get_users_collection()
    
    # Find user
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "region": user["region"],
        "created_at": user["created_at"]
    }

# ===================== CHAT ROUTES =====================

@app.post("/chat/messages", response_model=ChatResponse)
def send_message(message: ChatMessage):
    """
    Send a chat message and get AI response.
    
    Takes: user_id, conversation_id, text, language
    Returns: user message + AI response + timestamp
    """
    
    conversations_collection = get_conversations_collection()
    users_collection = get_users_collection()
    
    # Check if user exists
    user = users_collection.find_one({"user_id": message.user_id})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Get AI response
    ai_response = get_gemini_response(message.text)
    
    # Create message document
    message_data = {
        "user_id": message.user_id,
        "conversation_id": message.conversation_id,
        "user_message": message.text,
        "ai_response": ai_response,
        "timestamp": datetime.now().isoformat(),
        "language": message.language
    }
    
    # Save to MongoDB
    conversations_collection.insert_one(message_data)
    
    return {
        "user_message": message.text,
        "ai_response": ai_response,
        "timestamp": message_data["timestamp"]
    }

@app.get("/chat/conversations/{user_id}")
def get_conversations(user_id: str):
    """
    Get all conversations for a user.
    
    Takes: user_id
    Returns: List of all messages in chronological order
    """
    
    conversations_collection = get_conversations_collection()
    users_collection = get_users_collection()
    
    # Check if user exists
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Get all messages for this user
    messages = list(conversations_collection.find(
        {"user_id": user_id},
        {"_id": 0}  # Exclude MongoDB ID
    ).sort("timestamp", 1))  # Sort by timestamp ascending
    
    return {
        "user_id": user_id,
        "message_count": len(messages),
        "messages": messages
    }

@app.get("/chat/conversations/{user_id}/{conversation_id}")
def get_conversation(user_id: str, conversation_id: str):
    """
    Get specific conversation by ID.
    
    Takes: user_id, conversation_id
    Returns: All messages in that conversation
    """
    
    conversations_collection = get_conversations_collection()
    
    # Get all messages for this conversation
    messages = list(conversations_collection.find(
        {"user_id": user_id, "conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1))
    
    if not messages:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "message_count": len(messages),
        "messages": messages
    }

# ===================== RUN SERVER =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)