# ReVaani Backend API

## Setup Instructions for Team

### 1. Clone Repository
```bash
git clone https://github.com/durva-1/Revaani.git
cd Revaani/backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment
- Copy `.env.example` to `.env`
- Ask Asmi for the MongoDB connection URL
- Replace `USERNAME:PASSWORD@CLUSTER_NAME` with actual values

### 4. Run Server
```bash
python -m uvicorn main:app --reload
```

Server will run on: `http://localhost:8000`

### 5. Test API
Go to: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login and get token
- `GET /user/profile/{user_id}` — Get user profile

### Chat
- `POST /chat/messages` — Send message, get response
- `GET /chat/conversations/{user_id}` — Get all conversations
- `GET /chat/conversations/{user_id}/{conversation_id}` — Get specific chat

### Dataset
- `GET /dataset/sentences` — Get Gujarati sentences to read
- `POST /dataset/recordings` — Submit speech recording
- `GET /dataset/my-contributions/{user_id}` — Get user's contributions
- `GET /dataset/stats` — Dataset collection statistics

### System
- `GET /health` — API health check

## Current Status

Working Endpoints:
- User authentication (register, login, profile)
- Chat messaging with Gujarati responses
- MongoDB database integration

⏳ Coming Soon:
- Real Gemini API integration
- Dataset recording endpoints
- Speech-to-text (Whisper)
- Text-to-speech

## Testing the API

1. Register a user via `/auth/register`
2. Use that user_id in `/chat/messages`
3. Send Gujarati text, get Gujarati response
4. Messages saved in MongoDB

## Database
MongoDB Atlas (free tier, 512 MB storage)

Collections:
- users
- conversations
- recordings
- dataset_exports
- admin_logs
- analytics_events
