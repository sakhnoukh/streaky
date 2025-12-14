import { useState, useEffect } from 'react'
import axios from 'axios'
import './JournalDialog.css'

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '/api' : 'http://localhost:8002')

function JournalDialog({ habit, entryDate, onClose, onSave }) {
  const [journal, setJournal] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (entryDate) {
      fetchJournal()
    }
  }, [habit.id, entryDate])

  const fetchJournal = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.get(
        `${API_URL}/habits/${habit.id}/entries/${entryDate}`
      )
      setJournal(response.data.journal || '')
    } catch (err) {
      if (err.response?.status === 404) {
        // Entry doesn't exist yet, that's okay
        setJournal('')
      } else {
        setError('Failed to load journal entry')
        console.error('Journal fetch error:', err)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)

      // First, ensure the entry exists
      await axios.post(`${API_URL}/habits/${habit.id}/entries`, {
        date: entryDate,
        journal: journal || null
      })

      // Then update the journal if needed
      if (journal.trim()) {
        await axios.put(
          `${API_URL}/habits/${habit.id}/entries/${entryDate}/journal`,
          { journal: journal.trim() || null }
        )
      }

      if (onSave) {
        onSave()
      }
      onClose()
    } catch (err) {
      setError('Failed to save journal entry')
      console.error('Journal save error:', err)
    } finally {
      setSaving(false)
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div className="journal-overlay" onClick={onClose}>
      <div className="journal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="journal-header">
          <h3>{habit.name}</h3>
          <button className="journal-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="journal-date">{formatDate(entryDate)}</div>

        {loading && (
          <div className="journal-loading">Loading...</div>
        )}

        {error && (
          <div className="journal-error">{error}</div>
        )}

        {!loading && (
          <>
            <div className="journal-content">
              <textarea
                className="journal-textarea"
                placeholder="Write your thoughts about this entry..."
                value={journal}
                onChange={(e) => setJournal(e.target.value)}
                rows={10}
              />
            </div>

            <div className="journal-actions">
              <button
                className="journal-cancel-btn"
                onClick={onClose}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                className="journal-save-btn"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default JournalDialog
