function HabitList({ habits, onLogEntry, onEdit, onDelete, onViewCalendar }) {
  if (habits.length === 0) {
    return (
      <div className="empty-state">
        <h3>No habits yet</h3>
        <p>Create your first habit to get started!</p>
      </div>
    )
  }

  return (
    <div className="habit-list">
      <h2>My Habits</h2>
      <div className="habits-grid">
        {habits.map((habit) => (
          <div key={habit.id} className="habit-card">
            <div className="habit-header">
              <h3>{habit.name}</h3>
              <div className="habit-actions">
                <button
                  onClick={() => onEdit(habit)}
                  className="action-btn edit-btn"
                  title="Edit habit"
                >
                  ✏️
                </button>
                <button
                  onClick={() => onDelete(habit)}
                  className="action-btn delete-btn"
                  title="Delete habit"
                >
                  🗑️
                </button>
              </div>
            </div>
            
            <span className="goal-badge">{habit.goal_type}</span>
            
            <div className="habit-stats">
              <div className="stat-item">
                <span className="stat-icon">🔥</span>
                <div className="stat-content">
                  <span className="stat-number">{habit.streak}</span>
                  <span className="stat-label">Current</span>
                </div>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-icon">⭐</span>
                <div className="stat-content">
                  <span className="stat-number">{habit.best_streak}</span>
                  <span className="stat-label">Best</span>
                </div>
              </div>
            </div>

            <div className="habit-actions-bottom">
              <button
                onClick={() => onViewCalendar(habit)}
                className="calendar-btn"
                title="View calendar"
              >
                📅 Calendar
              </button>
              <button
                onClick={() => onLogEntry(habit.id)}
                className="log-btn"
              >
                ✓ Log Today
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HabitList
