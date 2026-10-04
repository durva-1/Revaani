# ReVaani Frontend

Simple, single-file HTML frontend for ReVaani Gujarati AI Assistant.

## How to run

```bash
# Start backend (port 8000)
cd ../backend
python -m uvicorn main:app --reload

# In another terminal, start frontend (port 8080)
cd ../frontend
python -m http.server 8080
```

Open: `http://localhost:8080/index.html`

## Features

- Clean dark UI
- Real-time Gujarati chat
- Integration with Gemini API
- Voice recording UI (coming soon)
- Single HTML file (no build process)