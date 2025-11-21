import { useState } from 'react'
import './EditHabit.css'

function EditHabit({ habit, onUpdate, onCancel }) {
  const [name, setName] = useState(habit.name)
  const [goalType, setGoalType] = useState(habit.goal_type)

  const handleSubmit = (e) => {
    e.preventDefault()
    onUpdate(habit.id, name, goalType)
  }

  return (
    <div className="edit-overlay" onClick={onCancel}>
      <div className="edit-dialog" onClick={(e) => e.stopPropagation()}>
        <h3>Edit Habit</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="edit-name">Habit Name</label>
            <input
              type="text"
              id="edit-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="edit-goal-type">Goal Type</label>
            <select
              id="edit-goal-type"
              value={goalType}
              onChange={(e) => setGoalType(e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          <div className="edit-actions">
            <button type="button" className="btn-cancel" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-save">
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EditHabit
