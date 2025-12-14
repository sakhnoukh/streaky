import { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import HabitList from './components/HabitList'
import AddHabit from './components/AddHabit'
import EditHabit from './components/EditHabit'
import ConfirmDialog from './components/ConfirmDialog'
import Calendar from './components/Calendar'
import Toast from './components/Toast'
import TodaySummary from './components/TodaySummary'
import CategoryManager from './components/CategoryManager'
import CategoryFilter from './components/CategoryFilter'
import HabitCategoryAssign from './components/HabitCategoryAssign'
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
  const [viewingCalendar, setViewingCalendar] = useState(null)
  const [categories, setCategories] = useState([])
  const [showCategoryManager, setShowCategoryManager] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [assigningCategories, setAssigningCategories] = useState(null)

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }, [token])

  // Fetch habits and categories when logged in
  useEffect(() => {
    if (token) {
      fetchHabits()
      fetchCategories()
    }
  }, [token])

  // Refetch habits when category filter changes
  useEffect(() => {
    if (token) {
      fetchHabits()
    }
  }, [selectedCategory])

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
    setCategories([])
    setSelectedCategory(null)
  }

  const fetchHabits = async () => {
    try {
      setLoading(true)
      setError(null)
      const params = selectedCategory ? { category_id: selectedCategory } : {}
      const response = await axios.get(`${API_URL}/habits`, { params })
      setHabits(response.data)
    } catch (err) {
      setError('Failed to fetch habits')
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/categories`)
      setCategories(response.data)
    } catch (err) {
      console.error('Fetch categories error:', err)
    }
  }

  const handleAddCategory = async (name, color) => {
    try {
      await axios.post(`${API_URL}/categories`, { name, color })
      await fetchCategories()
      showToast('Category created! 📁', 'success')
    } catch (err) {
      if (err.response?.status === 409) {
        showToast('Category name already exists', 'error')
      } else {
        showToast('Failed to create category', 'error')
      }
      console.error('Create category error:', err)
    }
  }

  const handleUpdateCategory = async (categoryId, name, color) => {
    try {
      await axios.put(`${API_URL}/categories/${categoryId}`, { name, color })
      await fetchCategories()
      await fetchHabits()
      showToast('Category updated! ✓', 'success')
    } catch (err) {
      showToast('Failed to update category', 'error')
      console.error('Update category error:', err)
    }
  }

  const handleDeleteCategory = async (categoryId) => {
    try {
      await axios.delete(`${API_URL}/categories/${categoryId}`)
      await fetchCategories()
      await fetchHabits()
      if (selectedCategory === categoryId) {
        setSelectedCategory(null)
      }
      showToast('Category deleted', 'info')
    } catch (err) {
      showToast('Failed to delete category', 'error')
      console.error('Delete category error:', err)
    }
  }

  const handleAddHabitToCategory = async (habitId, categoryId) => {
    try {
      await axios.post(`${API_URL}/categories/${categoryId}/habits/${habitId}`)
      await fetchHabits()
      // Update the assigning habit with new categories
      const updatedHabit = habits.find(h => h.id === habitId)
      if (updatedHabit) {
        const cat = categories.find(c => c.id === categoryId)
        if (cat) {
          setAssigningCategories({
            ...updatedHabit,
            categories: [...(updatedHabit.categories || []), cat]
          })
        }
      }
      showToast('Category added to habit! 🏷️', 'success')
    } catch (err) {
      showToast('Failed to add category', 'error')
      console.error('Add habit to category error:', err)
    }
  }

  const handleRemoveHabitFromCategory = async (habitId, categoryId) => {
    try {
      await axios.delete(`${API_URL}/categories/${categoryId}/habits/${habitId}`)
      await fetchHabits()
      // Update the assigning habit with removed category
      if (assigningCategories && assigningCategories.id === habitId) {
        setAssigningCategories({
          ...assigningCategories,
          categories: assigningCategories.categories.filter(c => c.id !== categoryId)
        })
      }
      showToast('Category removed from habit', 'info')
    } catch (err) {
      showToast('Failed to remove category', 'error')
      console.error('Remove habit from category error:', err)
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
        <div className="header-actions">
          <button onClick={() => setShowCategoryManager(true)} className="manage-categories-btn">
            📁 Categories
          </button>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="App-main">
        <TodaySummary habits={habits} />
        
        {categories.length > 0 && (
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
        )}
        
        <AddHabit onAdd={handleAddHabit} />
        
        {loading ? (
          <div className="loading">Loading habits...</div>
        ) : (
          <HabitList 
            habits={habits} 
            onLogEntry={handleLogEntry}
            onEdit={setEditingHabit}
            onDelete={setDeletingHabit}
            onViewCalendar={setViewingCalendar}
            onManageCategories={setAssigningCategories}
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

      {viewingCalendar && (
        <Calendar
          habit={viewingCalendar}
          onClose={() => {
            setViewingCalendar(null)
            fetchHabits() // Refresh habits to update any changes
          }}
        />
      )}

      {showCategoryManager && (
        <CategoryManager
          categories={categories}
          onAdd={handleAddCategory}
          onUpdate={handleUpdateCategory}
          onDelete={handleDeleteCategory}
          onClose={() => setShowCategoryManager(false)}
        />
      )}

      {assigningCategories && (
        <HabitCategoryAssign
          habit={assigningCategories}
          categories={categories}
          onAddCategory={handleAddHabitToCategory}
          onRemoveCategory={handleRemoveHabitFromCategory}
          onClose={() => setAssigningCategories(null)}
        />
      )}
    </div>
  )
}

export default App
