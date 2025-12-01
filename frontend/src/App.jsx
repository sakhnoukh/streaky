import { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import HabitList from './components/HabitList'
import AddHabit from './components/AddHabit'
import EditHabit from './components/EditHabit'
import ConfirmDialog from './components/ConfirmDialog'
import Toast from './components/Toast'
import './App.css'

// Use environment variable for API URL, fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [habits, setHabits] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [editingHabit, setEditingHabit] = useState(null)
  const [deletingHabit, setDeletingHabit] = useState(null)

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

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
  }

  const handleRegister = async (username, password) => {
    try {
      setError(null)
      console.log('Registering with API:', API_URL)
      await axios.post(`${API_URL}/auth/register`, {
        username,
        password
      })
      
      // Auto-login after successful registration
      showToast('Account created! Logging you in... 🎉', 'success')
      setTimeout(() => handleLogin(username, password), 500)
    } catch (err) {
      console.error('Register error:', err)
      if (err.response?.status === 409) {
        setError('Username already exists. Please choose another.')
      } else if (err.response?.data?.detail) {
        setError(`Registration failed: ${err.response.data.detail}`)
      } else if (err.code === 'ERR_NETWORK') {
        setError(`Cannot connect to server. API URL: ${API_URL}`)
      } else {
        setError(`Registration failed: ${err.message || 'Unknown error'}`)
      }
    }
  }

  const handleLogin = async (username, password) => {
    try {
      setError(null)
      console.log('Logging in with API:', API_URL)
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
      showToast('Welcome back! 🎯', 'success')
    } catch (err) {
      console.error('Login error:', err)
      if (err.response?.data?.detail) {
        setError(`Login failed: ${err.response.data.detail}`)
      } else if (err.code === 'ERR_NETWORK') {
        setError(`Cannot connect to server. API URL: ${API_URL}`)
      } else {
        setError(`Login failed: ${err.message || 'Please check your credentials.'}`)
      }
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
      await fetchHabits()
      showToast('Habit created successfully! 🎉', 'success')
    } catch (err) {
      if (err.response?.status === 409) {
        showToast('Habit name already exists', 'error')
      } else {
        showToast('Failed to create habit', 'error')
      }
      console.error('Create habit error:', err)
    }
  }

  const handleUpdateHabit = async (habitId, name, goalType) => {
    try {
      await axios.put(`${API_URL}/habits/${habitId}`, {
        name,
        goal_type: goalType
      })
      await fetchHabits()
      setEditingHabit(null)
      showToast('Habit updated successfully! ✓', 'success')
    } catch (err) {
      showToast('Failed to update habit', 'error')
      console.error('Update habit error:', err)
    }
  }

  const handleDeleteHabit = async (habitId) => {
    try {
      await axios.delete(`${API_URL}/habits/${habitId}`)
      await fetchHabits()
      setDeletingHabit(null)
      showToast('Habit deleted', 'info')
    } catch (err) {
      showToast('Failed to delete habit', 'error')
      console.error('Delete habit error:', err)
    }
  }

  const handleLogEntry = async (habitId) => {
    try {
      setError(null)
      const today = new Date().toISOString().split('T')[0]
      await axios.post(`${API_URL}/habits/${habitId}/entries`, {
        date: today
      })
      await fetchHabits()
      showToast('Entry logged! 🔥', 'success')
    } catch (err) {
      showToast('Failed to log entry', 'error')
      console.error('Log entry error:', err)
    }
  }

  if (!token) {
    return <Login onLogin={handleLogin} onRegister={handleRegister} error={error} />
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
        <AddHabit onAdd={handleAddHabit} />
        
        {loading ? (
          <div className="loading">Loading habits...</div>
        ) : (
          <HabitList 
            habits={habits} 
            onLogEntry={handleLogEntry}
            onEdit={setEditingHabit}
            onDelete={setDeletingHabit}
          />
        )}
      </main>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {editingHabit && (
        <EditHabit
          habit={editingHabit}
          onUpdate={handleUpdateHabit}
          onCancel={() => setEditingHabit(null)}
        />
      )}

      {deletingHabit && (
        <ConfirmDialog
          title="Delete Habit?"
          message={`Are you sure you want to delete "${deletingHabit.name}"? This action cannot be undone.`}
          onConfirm={() => handleDeleteHabit(deletingHabit.id)}
          onCancel={() => setDeletingHabit(null)}
          confirmText="Delete"
          confirmType="danger"
        />
      )}
    </div>
  )
}

export default App
