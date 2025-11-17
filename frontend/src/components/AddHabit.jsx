import { useState } from 'react'

function AddHabit({ onAdd }) {
  const [name, setName] = useState('')
  const [goalType, setGoalType] = useState('daily')
  const [isOpen, setIsOpen] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (name.trim()) {
      onAdd(name, goalType)
      setName('')
      setGoalType('daily')
      setIsOpen(false)
    }
  }

  if (!isOpen) {
    return (
      <button onClick={() => setIsOpen(true)} className="add-habit-toggle">
        + Add New Habit
      </button>
    )
  }

  return (
    <div className="add-habit-card">
      <h3>Create New Habit</h3>
      <form onSubmit={handleSubmit} className="add-habit-form">
        <div className="form-group">
          <label htmlFor="habit-name">Habit Name</label>
          <input
            type="text"
            id="habit-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Morning Exercise"
            required
            autoFocus
          />
        </div>

        <div className="form-group">
          <label htmlFor="goal-type">Goal Type</label>
          <select
            id="goal-type"
            value={goalType}
            onChange={(e) => setGoalType(e.target.value)}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary">
            Create Habit
          </button>
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default AddHabit
