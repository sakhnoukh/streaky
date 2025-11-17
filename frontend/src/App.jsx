import { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import HabitList from './components/HabitList'
import AddHabit from './components/AddHabit'
import './App.css'

const API_URL = 'http://localhost:8002'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [habits, setHabits] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }, [token])

  // Fetch habits when logged in
  useEffect(() => {
    if (token) {
      fetchHabits()
    }
  }, [token])

  const handleLogin = async (username, password) => {
    try {
      setError(null)
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post(`${API_URL}/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
    } catch (err) {
      setError('Login failed. Please check your credentials.')
      console.error('Login error:', err)
    }
  }

  const handleLogout = () => {
    setToken(null)
    localStorage.removeItem('token')
    setHabits([])
  }

  const fetchHabits = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.get(`${API_URL}/habits`)
      setHabits(response.data)
    } catch (err) {
      setError('Failed to fetch habits')
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddHabit = async (name, goalType) => {
    try {
      setError(null)
      await axios.post(`${API_URL}/habits`, {
        name,
        goal_type: goalType
      })
      fetchHabits()
    } catch (err) {
      if (err.response?.status === 409) {
        setError('Habit name already exists')
      } else {
        setError('Failed to create habit')
      }
      console.error('Create habit error:', err)
    }
  }

  const handleLogEntry = async (habitId) => {
    try {
      setError(null)
      const today = new Date().toISOString().split('T')[0]
      await axios.post(`${API_URL}/habits/${habitId}/entries`, {
        date: today
      })
      fetchHabits()
    } catch (err) {
      setError('Failed to log entry')
      console.error('Log entry error:', err)
    }
  }

  if (!token) {
    return <Login onLogin={handleLogin} error={error} />
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 Streaky</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </header>

      <main className="App-main">
        {error && <div className="error-message">{error}</div>}
        
        <AddHabit onAdd={handleAddHabit} />
        
        {loading ? (
          <div className="loading">Loading habits...</div>
        ) : (
          <HabitList habits={habits} onLogEntry={handleLogEntry} />
        )}
      </main>
    </div>
  )
}

export default App
