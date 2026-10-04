# ReVaani Backend API

ReVaani - AI Based Gujarati Accent Aware Voice Assistant

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
- Copy `env.example` to `.env`
- Ask Asmi for the MongoDB connection URL and the Gemini API key
- Replace the placeholder values in `.env` with the real values
- Generate your own JWT secret by running this command, and paste the output as `JWT_SECRET`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
- Never push `.env` to GitHub. It contains secret keys.

Your `.env` should have these 4 lines:
```
MONGODB_URL=...
DATABASE_NAME=...
GEMINI_API_KEY=...
JWT_SECRET=...
```

### 4. Run Backend Server
```bash
python -m uvicorn main:app --reload
```

Server will run on: `http://localhost:8000`

### 5. Run Frontend
Open a second terminal:
```bash
cd Revaani/frontend
python -m http.server 8080
```

Then open: `http://localhost:8080/index.html`

Use port 8080. The backend only allows requests from ports 8080, 5173 and 3000.

### 6. Test API
Go to: `http://localhost:8000/docs`

To test protected endpoints:
1. Run `POST /auth/login` and copy the `token` value
2. Click the green **Authorize** button
3. Paste only the token (without the word Bearer) and click Authorize

## API Endpoints

Endpoints marked (token) need a login token.

### Authentication
- `POST /auth/register` - Register new user, returns token
- `POST /auth/login` - Login, returns token
- `GET /user/profile` (token) - Get logged-in user's profile

### Chat
- `POST /chat/messages` (token) - Send message, get Gemini response
- `GET /chat/conversations` (token) - List all conversations of the logged-in user
- `GET /chat/conversations/{conversation_id}` (token) - Get all messages of one conversation
- `DELETE /chat/conversations/{conversation_id}` (token) - Delete one conversation

### Dataset (backend ready, not connected to the frontend yet)
- `GET /dataset/sentences` - Get Gujarati sentences to read
- `POST /dataset/recordings` - Submit speech recording
- `GET /dataset/my-contributions/{user_id}` - Get user's contributions
- `GET /dataset/stats` - Dataset collection statistics

### System
- `GET /health` - API health check

## Current Status

Working:
- User registration and login (bcrypt password hashing, JWT token valid for 24 hours)
- Chat with Gemini, Gujarati responses
- Chat history: list, open and delete conversations
- Frontend: login/signup screen, chat screen, history sidebar, logout
- MongoDB Atlas integration

Not done yet:
- Speech-to-text (Whisper)
- Text-to-speech
- Dataset recording page in the frontend
- Token protection for dataset endpoints
- Admin review of recordings
- Refresh token

## Testing the App

1. Open the frontend and click "Create account"
2. Register with your name, region, email and password
3. Type a Gujarati message and send it
4. The reply appears, and the chat shows in the left sidebar
5. Refresh the page. You stay logged in and your history is still there

## Database
MongoDB Atlas (free tier, 512 MB storage)

Collections currently used:
- users
- conversations
- recordings

Planned (not implemented yet):
- dataset_exports
- admin_logs
- analytics_events
