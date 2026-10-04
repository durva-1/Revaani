from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import secrets
import os
from dotenv import load_dotenv
from database import get_users_collection, get_conversations_collection, get_recordings_collection
from auth import hash_password, verify_password, create_token, decode_token

load_dotenv()

app = FastAPI(
    title="ReVaani API",
    description="Gujarati Accent-Aware Voice Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    region: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    region: str
    created_at: str


class ChatMessage(BaseModel):
    conversation_id: Optional[str] = None
    text: str
    language: str = "gujarati"


class DatasetSentence(BaseModel):
    sentence_id: str
    gujarati_text: str
    english_translation: str
    difficulty: str


class RecordingMetadata(BaseModel):
    user_id: str
    sentence_id: str
    region: str
    age_group: str
    gender: str
    accent: str
    duration_seconds: float
    audio_quality_score: float


class RecordingResponse(BaseModel):
    recording_id: str
    user_id: str
    status: str
    created_at: str


security = HTTPBearer(auto_error=False)


def generate_user_id() -> str:
    return secrets.token_hex(12)


def generate_conversation_id() -> str:
    return secrets.token_hex(12)


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Please login first")

    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload["sub"]


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


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "ReVaani API is running",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/auth/register")
def register(request: RegisterRequest):
    users_collection = get_users_collection()
    email = request.email.lower()

    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user_id = generate_user_id()
    user_data = {
        "user_id": user_id,
        "email": email,
        "password_hash": hash_password(request.password),
        "full_name": request.full_name,
        "region": request.region,
        "created_at": datetime.now().isoformat(),
        "is_admin": False,
        "is_active": True
    }

    users_collection.insert_one(user_data)

    token = create_token(user_id, email)

    return {
        "token": token,
        "user_id": user_id,
        "email": email,
        "full_name": request.full_name,
        "region": request.region
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    users_collection = get_users_collection()
    email = request.email.lower()

    user = users_collection.find_one({"email": email})
    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["user_id"], email)

    return {
        "token": token,
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "message": "Login successful"
    }


@app.get("/user/profile", response_model=UserResponse)
def get_user_profile(user_id: str = Depends(get_current_user_id)):
    user = get_users_collection().find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "region": user["region"],
        "created_at": user["created_at"]
    }


@app.post("/chat/messages")
def send_message(request: ChatMessage, user_id: str = Depends(get_current_user_id)):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="No message provided")

    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = generate_conversation_id()

    ai_response = get_gemini_response(request.text)

    get_conversations_collection().insert_one({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message": request.text,
        "ai_response": ai_response,
        "language": request.language,
        "timestamp": datetime.utcnow()
    })

    return {
        "conversation_id": conversation_id,
        "user_message": request.text,
        "ai_response": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }


def get_last_updated(conversation):
    return conversation["last_updated"]


@app.get("/chat/conversations")
def get_conversations(user_id: str = Depends(get_current_user_id)):
    messages = list(get_conversations_collection().find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", 1))

    conversations = {}
    for m in messages:
        cid = m["conversation_id"]
        if cid not in conversations:
            conversations[cid] = {
                "conversation_id": cid,
                "title": m["message"][:40],
                "message_count": 0,
                "last_updated": ""
            }
        conversations[cid]["message_count"] += 1
        conversations[cid]["last_updated"] = str(m["timestamp"])

    result = list(conversations.values())
    result.sort(key=get_last_updated, reverse=True)

    return {"conversations": result}


@app.get("/chat/conversations/{conversation_id}")
def get_conversation(conversation_id: str, user_id: str = Depends(get_current_user_id)):
    messages = list(get_conversations_collection().find(
        {"user_id": user_id, "conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1))

    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "message_count": len(messages),
        "messages": messages
    }


@app.delete("/chat/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, user_id: str = Depends(get_current_user_id)):
    result = get_conversations_collection().delete_many(
        {"user_id": user_id, "conversation_id": conversation_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted"}


@app.get("/dataset/sentences")
def get_dataset_sentences():
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
    import base64

    users_collection = get_users_collection()
    recordings_collection = get_recordings_collection()

    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sentence = next((s for s in GUJARATI_SENTENCES if s["sentence_id"] == sentence_id), None)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    audio_content = await file.read()
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')

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
        "audio_file": audio_base64,
        "file_name": file.filename,
        "file_size_bytes": len(audio_content),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "admin_notes": ""
    }

    recordings_collection.insert_one(recording_data)

    return {
        "recording_id": recording_id,
        "user_id": user_id,
        "status": "pending",
        "created_at": recording_data["created_at"]
    }


@app.get("/dataset/my-contributions/{user_id}")
def get_my_contributions(user_id: str):
    users_collection = get_users_collection()
    recordings_collection = get_recordings_collection()

    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recordings = list(recordings_collection.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1))

    return {
        "user_id": user_id,
        "total_contributions": len(recordings),
        "recordings": recordings
    }


@app.get("/dataset/stats")
def get_dataset_stats():
    recordings_collection = get_recordings_collection()

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)