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

- `GET /health` — Check if API is running
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login user
- `GET /user/profile/{user_id}` — Get user profile

## Database
MongoDB Atlas (free tier, 512 MB storage)

Collections:
- users
- conversations
- recordings
- dataset_exports
- admin_logs
- analytics_events