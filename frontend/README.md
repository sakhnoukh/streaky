# Streaky Frontend

React-based frontend for the Streaky habit tracker application.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool & dev server
- **Axios** - HTTP client
- **CSS3** - Styling

## Quick Start

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at **http://localhost:3000**

## Features

- 🔐 **Login** - JWT authentication
- ➕ **Create Habits** - Daily or weekly goals
- 📝 **Log Entries** - Track completion
- 🔥 **View Streaks** - See current streak for each habit
- 📱 **Responsive** - Works on desktop and mobile

## Usage

1. **Login**
   - Default credentials: `testuser` / `testpass`
   - Token stored in localStorage

2. **Create a Habit**
   - Click "+ Add New Habit"
   - Enter name and select goal type (daily/weekly)
   - Click "Create Habit"

3. **Log Today's Entry**
   - Click "✓ Log Today" on any habit card
   - Streak updates automatically

4. **View Streaks**
   - Each habit card shows current streak
   - 🔥 emoji with streak count

## API Configuration

The frontend expects the backend API at **http://localhost:8002**

To change this, edit `src/App.jsx`:
```javascript
const API_URL = 'http://localhost:8002'  // Change this
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx        # Login form
│   │   ├── HabitList.jsx    # Display habits grid
│   │   └── AddHabit.jsx     # Create new habit
│   ├── App.jsx              # Main app logic
│   ├── App.css              # Styling
│   ├── main.jsx             # React entry point
│   └── index.css            # Global styles
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
└── package.json             # Dependencies
```

## Development

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment

- **Dev server:** http://localhost:3000
- **API endpoint:** http://localhost:8002
- **Token storage:** localStorage (key: 'token')

## Design

- Beautiful gradient background (purple)
- Card-based UI
- Smooth animations and transitions
- Mobile-responsive grid layout
- Clean, modern aesthetic

## Future Enhancements

- [ ] Statistics view (7-day/30-day charts)
- [ ] Edit/delete habits
- [ ] Date picker for backfilling entries
- [ ] Best streak display
- [ ] Dark mode toggle
- [ ] Habit categories/tags
- [ ] Achievement badges
