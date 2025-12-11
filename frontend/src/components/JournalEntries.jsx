import { useState, useEffect } from 'react'
import axios from 'axios'
import JournalDialog from './JournalDialog'
import './JournalEntries.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

function JournalEntries({ habit, onClose }) {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedEntry, setSelectedEntry] = useState(null)

  useEffect(() => {
    fetchEntries()
  }, [habit.id])

  const fetchEntries = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.get(`${API_URL}/habits/${habit.id}/entries`)
      setEntries(response.data)
    } catch (err) {
      setError('Failed to load journal entries')
      console.error('Journal entries fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEntryClick = (entry) => {
    setSelectedEntry({ habit, date: entry.date })
  }

  const handleJournalSave = () => {
    fetchEntries() // Refresh entries after saving
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    // Check if it's today
    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    }
    // Check if it's yesterday
    if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    }
    // Otherwise return formatted date
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatTime = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <div className="journal-entries-overlay" onClick={onClose}>
      <div className="journal-entries-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="journal-entries-header">
          <div>
            <h3>{habit.name} - Journal Entries</h3>
            <p className="journal-entries-subtitle">
              {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
            </p>
          </div>
          <button className="journal-entries-close-btn" onClick={onClose}>✕</button>
        </div>

        {loading && (
          <div className="journal-entries-loading">Loading entries...</div>
        )}

        {error && (
          <div className="journal-entries-error">{error}</div>
        )}

        {!loading && !error && (
          <div className="journal-entries-content">
            {entries.length === 0 ? (
              <div className="journal-entries-empty">
                <div className="journal-entries-empty-icon">📝</div>
                <h4>No journal entries yet</h4>
                <p>Start logging your habit and add journal entries to track your journey!</p>
              </div>
            ) : (
              <div className="journal-entries-list">
                {entries.map((entry) => (
                  <div
                    key={entry.id}
                    className="journal-entry-item"
                    onClick={() => handleEntryClick(entry)}
                  >
                    <div className="journal-entry-date">
                      <span className="journal-entry-date-main">{formatDate(entry.date)}</span>
                      <span className="journal-entry-date-sub">{formatTime(entry.date)}</span>
                    </div>
                    <div className="journal-entry-content">
                      {entry.journal ? (
                        <p className="journal-entry-text">{entry.journal}</p>
                      ) : (
                        <p className="journal-entry-empty">No journal entry - click to add one</p>
                      )}
                    </div>
                    <div className="journal-entry-arrow">→</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {selectedEntry && (
          <JournalDialog
            habit={selectedEntry.habit}
            entryDate={selectedEntry.date}
            onClose={() => setSelectedEntry(null)}
            onSave={handleJournalSave}
          />
        )}
      </div>
    </div>
  )
}

export default JournalEntries
