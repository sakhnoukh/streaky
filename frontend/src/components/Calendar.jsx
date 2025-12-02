import { useState, useEffect } from 'react'
import axios from 'axios'
import './Calendar.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function Calendar({ habit, onClose }) {
  const [calendarData, setCalendarData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const today = new Date()
  const [currentDate, setCurrentDate] = useState({
    year: today.getFullYear(),
    month: today.getMonth() + 1
  })

  useEffect(() => {
    fetchCalendarData()
  }, [habit.id, currentDate.year, currentDate.month])

  const fetchCalendarData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.get(
        `${API_URL}/habits/${habit.id}/calendar?year=${currentDate.year}&month=${currentDate.month}`
      )
      setCalendarData(response.data)
    } catch (err) {
      setError('Failed to load calendar data')
      console.error('Calendar fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      let newMonth = prev.month + direction
      let newYear = prev.year

      if (newMonth > 12) {
        newMonth = 1
        newYear += 1
      } else if (newMonth < 1) {
        newMonth = 12
        newYear -= 1
      }

      return { year: newYear, month: newMonth }
    })
  }

  const goToToday = () => {
    setCurrentDate({
      year: today.getFullYear(),
      month: today.getMonth() + 1
    })
  }

  // Generate calendar grid
  const generateCalendarGrid = () => {
    if (!calendarData) return []

    const { year, month, days } = calendarData
    const firstDay = new Date(year, month - 1, 1)
    const lastDay = new Date(year, month, 0)
    const startDayOfWeek = firstDay.getDay()
    const daysInMonth = lastDay.getDate()

    // Create a map of dates to completion status
    const dateMap = {}
    days.forEach(day => {
      dateMap[day.date] = day.completed
    })

    const grid = []
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startDayOfWeek; i++) {
      grid.push({ date: null, completed: false })
    }

    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      grid.push({
        date: day,
        dateStr,
        completed: dateMap[dateStr] || false
      })
    }

    return grid
  }

  const isToday = (day) => {
    if (!day) return false
    const todayStr = today.toISOString().split('T')[0]
    return day.dateStr === todayStr
  }

  return (
    <div className="calendar-overlay" onClick={onClose}>
      <div className="calendar-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="calendar-header">
          <h3>{habit.name} - Calendar</h3>
          <button className="calendar-close-btn" onClick={onClose}>✕</button>
        </div>

        {loading && (
          <div className="calendar-loading">Loading calendar...</div>
        )}

        {error && (
          <div className="calendar-error">{error}</div>
        )}

        {!loading && !error && calendarData && (
          <>
            <div className="calendar-controls">
              <button className="calendar-nav-btn" onClick={() => navigateMonth(-1)}>
                ←
              </button>
              <div className="calendar-month-year">
                <span className="calendar-month">{MONTH_NAMES[currentDate.month - 1]}</span>
                <span className="calendar-year">{currentDate.year}</span>
              </div>
              <button className="calendar-nav-btn" onClick={() => navigateMonth(1)}>
                →
              </button>
              <button className="calendar-today-btn" onClick={goToToday}>
                Today
              </button>
            </div>

            <div className="calendar-grid-container">
              <div className="calendar-day-headers">
                {DAY_NAMES.map(day => (
                  <div key={day} className="calendar-day-header">{day}</div>
                ))}
              </div>

              <div className="calendar-grid">
                {generateCalendarGrid().map((day, index) => (
                  <div
                    key={index}
                    className={`calendar-day ${day.date ? '' : 'calendar-day-empty'} ${day.completed ? 'calendar-day-completed' : ''} ${isToday(day) ? 'calendar-day-today' : ''}`}
                    title={day.dateStr}
                  >
                    {day.date && (
                      <>
                        <span className="calendar-day-number">{day.date}</span>
                        {day.completed && <span className="calendar-check">✓</span>}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="calendar-legend">
              <div className="legend-item">
                <div className="legend-box calendar-day-completed"></div>
                <span>Completed</span>
              </div>
              <div className="legend-item">
                <div className="legend-box calendar-day-today"></div>
                <span>Today</span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Calendar

