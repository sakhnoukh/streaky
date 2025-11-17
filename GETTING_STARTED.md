# Getting Started with Streaky

Complete guide to run both the backend API and React frontend.

## 📋 Prerequisites

- **Python 3.13+** (backend)
- **Node.js 18+** and npm (frontend)
- Terminal/Command line

## 🚀 Quick Start (Both Backend + Frontend)

### Step 1: Start the Backend API

```bash
# Navigate to project root
cd /Users/samiakhnoukh/Documents/UNI/Year\ 3/Semester\ 1/DevOps/Assignments/streaky

# Activate virtual environment
source .env/bin/activate

# Start the API server on port 8002
uvicorn app.main:app --reload --port 8002
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8002
INFO:     Application startup complete.
```

✅ Backend is ready! Leave this terminal open.

---

### Step 2: Start the Frontend (NEW TERMINAL)

Open a **second terminal window**:

```bash
# Navigate to frontend directory
cd /Users/samiakhnoukh/Documents/UNI/Year\ 3/Semester\ 1/DevOps/Assignments/streaky/frontend

# Install dependencies (first time only)
npm install

# Start React dev server
npm run dev
```

**Expected output:**
```
  VITE v5.1.0  ready in 500 ms

  ➜  Local:   http://localhost:5000/
  ➜  Network: use --host to expose
```

✅ Frontend is ready!

---

### Step 3: Open the App

Open your browser to: **http://localhost:5000**

You should see the Streaky login page! 🎉

**Login credentials:**
- Username: `testuser`
- Password: `testpass`

---

## 🎯 What You Can Do

### 1. **Login**
- Enter credentials
- Token is saved automatically

### 2. **Create Your First Habit**
- Click "+ Add New Habit"
- Enter name (e.g., "Morning Exercise")
- Choose goal type (daily or weekly)
- Click "Create Habit"

### 3. **Log Today's Entry**
- Click "✓ Log Today" on any habit card
- Watch your streak increase! 🔥

### 4. **Track Your Progress**
- Each habit card shows current streak
- Streak updates immediately after logging

---

## 📁 Project Structure

```
streaky/
├── app/                    # Backend (Python/FastAPI)
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── repositories/      # Database access
│   └── models.py          # Database models
│
├── frontend/              # Frontend (React/Vite)
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.jsx       # Main app
│   │   └── App.css       # Styling
│   └── package.json      # Dependencies
│
├── tests/                 # Backend tests
└── README.md             # Full documentation
```

---

## 🔧 Common Issues

### Backend won't start?

**Problem:** Port 8002 already in use
```bash
# Find and kill process on port 8002
lsof -ti:8002 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8003
```

### Frontend can't connect to backend?

**Check:**
1. Is backend running? Visit http://localhost:8002/healthz
2. Should return `{"ok": true}`
3. Check browser console for errors (F12)

### Login not working?

**Verify:**
- Backend is running on port 8002
- Using correct credentials: `testuser` / `testpass`
- Check browser console (F12) for error messages

---

## 🎨 UI Features

### Beautiful Design
- Gradient purple background
- Card-based layout
- Smooth animations
- Mobile responsive

### What's Shown
- **Habit Cards:** Display name, goal type, and streak
- **Streak Counter:** 🔥 emoji with number
- **Log Button:** Quick one-click logging
- **Add Form:** Simple habit creation

---

## 🔄 Development Workflow

### Making Backend Changes

```bash
# Backend auto-reloads on file changes
# Just edit files in app/ directory
# Refresh browser to see changes
```

### Making Frontend Changes

```bash
# Vite auto-reloads on file changes
# Edit files in frontend/src/
# Browser refreshes automatically
```

### Running Tests

```bash
# Backend tests
cd /path/to/streaky
.env/bin/pytest

# 54 tests should pass
```

---

## 📊 API Access

While the UI is running, you can still access:

- **Swagger UI:** http://localhost:8002/docs
- **ReDoc:** http://localhost:8002/redoc
- **Health Check:** http://localhost:8002/healthz

---

## 🎓 Next Steps

### Try These:

1. **Create multiple habits**
   - Morning Exercise
   - Read 30 minutes
   - Drink 8 glasses of water

2. **Log entries for several days**
   - Build up your streaks!

3. **Test the API directly**
   - Open http://localhost:8002/docs
   - Try endpoints manually

### Future Enhancements:

- View 7-day/30-day statistics
- Edit or delete habits
- Best streak tracking
- Achievement badges
- Dark mode

---

## 🛑 Stopping the Servers

### Backend:
```bash
# In the backend terminal:
Ctrl + C
```

### Frontend:
```bash
# In the frontend terminal:
Ctrl + C
```

---

## 💡 Tips

1. **Keep both terminals open** while developing
2. **Backend logs** show all API requests
3. **Browser console** (F12) shows frontend errors
4. **Token expires** after 30 minutes - just login again
5. **Data persists** in SQLite database (`streaky.db`)

---

## 📚 More Documentation

- **Backend API:** See main [README.md](README.md)
- **Frontend:** See [frontend/README.md](frontend/README.md)
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## ✨ Summary

**To run everything:**

```bash
# Terminal 1 (Backend)
uvicorn app.main:app --reload --port 8002

# Terminal 2 (Frontend)
cd frontend && npm run dev

# Browser
http://localhost:5000
```

**That's it!** 🎉 You're now tracking habits with a beautiful UI!
