from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import hashlib
import secrets
import os
from dotenv import load_dotenv
from database import get_users_collection, get_conversations_collection, get_recordings_collection
from google.genai import types
import google.genai as genai
import base64
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

class DatasetSentence(BaseModel):
    """Gujarati sentence for dataset contribution"""
    sentence_id: str
    gujarati_text: str
    english_translation: str
    difficulty: str  # easy, medium, hard

class RecordingMetadata(BaseModel):
    """Recording metadata submission"""
    user_id: str
    sentence_id: str
    region: str  # e.g., "Ahmedabad", "Surat"
    age_group: str  # e.g., "18-25", "25-35"
    gender: str  # e.g., "male", "female", "other"
    accent: str  # optional
    duration_seconds: float  # audio length
    audio_quality_score: float  # 0.0 to 1.0

class RecordingResponse(BaseModel):
    """Recording response"""
    recording_id: str
    user_id: str
    status: str
    created_at: str

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
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash-lite')
        
        response = model.generate_content(user_message)
        
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "માફ કરો, એક ભૂલ આવી. કૃપયા ફરીથી પ્રયાસ કરો."
# Sample Gujarati sentences for dataset collection
GUJARATI_SENTENCES = [
    {
        "sentence_id": "sent_001",
        "gujarati_text": "નમસ્તે, આપ કેવા છો?",
        "english_translation": "Hello, how are you?",
        "difficulty": "easy"
    },
    {
        "sentence_id": "sent_002",
        "gujarati_text": "આજ બહુ સુંદર દિવસ છે.",
        "english_translation": "Today is a beautiful day.",
        "difficulty": "easy"
    },
    {
        "sentence_id": "sent_003",
        "gujarati_text": "હું ગુજરાતી શીખી રહ્યો છું.",
        "english_translation": "I am learning Gujarati.",
        "difficulty": "medium"
    },
    {
        "sentence_id": "sent_004",
        "gujarati_text": "આપનું નામ શું છે?",
        "english_translation": "What is your name?",
        "difficulty": "easy"
    },
    {
        "sentence_id": "sent_005",
        "gujarati_text": "આ ડેટાસેટ ભાષા સંશોધન માટે મહત્વપૂર્ણ છે.",
        "english_translation": "This dataset is important for language research.",
        "difficulty": "hard"
    }
]

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

# ===================== DATASET ROUTES =====================

@app.get("/dataset/sentences")
def get_dataset_sentences():
    """
    Get list of Gujarati sentences for dataset contribution.
    
    Users read these sentences and record themselves.
    Returns: List of sentences with translations
    """
    return {
        "total_sentences": len(GUJARATI_SENTENCES),
        "sentences": GUJARATI_SENTENCES
    }

@app.post("/dataset/recordings", response_model=RecordingResponse)
async def submit_recording(
    user_id: str,
    sentence_id: str,
    region: str,
    age_group: str,
    gender: str,
    accent: str,
    duration_seconds: float,
    audio_quality_score: float,
    file: UploadFile = File(...)
):
    """
    Submit a speech recording to the dataset with audio file.
    
    Takes: metadata (user_id, sentence_id, region, etc.) + audio file
    Returns: recording_id, status, created_at
    """
    import base64
    
    users_collection = get_users_collection()
    recordings_collection = get_recordings_collection()
    
    # Check if user exists
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if sentence exists
    sentence = next((s for s in GUJARATI_SENTENCES if s["sentence_id"] == sentence_id), None)
    if not sentence:
        raise HTTPException(
            status_code=404,
            detail="Sentence not found"
        )
    
    # Read and encode audio file
    audio_content = await file.read()
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    
    # Create recording document
    recording_id = generate_user_id()
    recording_data = {
        "recording_id": recording_id,
        "user_id": user_id,
        "sentence_id": sentence_id,
        "gujarati_text": sentence["gujarati_text"],
        "region": region,
        "age_group": age_group,
        "gender": gender,
        "accent": accent if accent else "Not specified",
        "duration_seconds": duration_seconds,
        "audio_quality_score": audio_quality_score,
        "audio_file": audio_base64,  # ← Audio stored as base64
        "file_name": file.filename,
        "file_size_bytes": len(audio_content),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "admin_notes": ""
    }
    
    # Save to MongoDB
    recordings_collection.insert_one(recording_data)
    
    return {
        "recording_id": recording_id,
        "user_id": user_id,
        "status": "pending",
        "created_at": recording_data["created_at"]
    }

@app.get("/dataset/my-contributions/{user_id}")
def get_my_contributions(user_id: str):
    """
    Get all recordings submitted by a user.
    
    Takes: user_id
    Returns: List of user's recordings
    """
    
    users_collection = get_users_collection()
    recordings_collection = get_recordings_collection()
    
    # Check if user exists
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Get all recordings for this user
    recordings = list(recordings_collection.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1))  # Most recent first
    
    return {
        "user_id": user_id,
        "total_contributions": len(recordings),
        "recordings": recordings
    }

@app.get("/dataset/stats")
def get_dataset_stats():
    """
    Get dataset collection statistics.
    
    Returns: Total recordings, pending, approved, by region, etc.
    """
    
    recordings_collection = get_recordings_collection()
    
    # Count statistics
    total = recordings_collection.count_documents({})
    pending = recordings_collection.count_documents({"status": "pending"})
    approved = recordings_collection.count_documents({"status": "approved"})
    
    return {
        "total_recordings": total,
        "pending_approval": pending,
        "approved": approved,
        "database_ready": True,
        "message": "Dataset collection system is ready"
    }

# ===================== RUN SERVER =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)