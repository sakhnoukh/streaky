function HabitList({ habits, onLogEntry }) {
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
              <span className="goal-badge">{habit.goal_type}</span>
            </div>
            
            <div className="habit-streak">
              <span className="streak-icon">🔥</span>
              <span className="streak-number">{habit.streak}</span>
              <span className="streak-label">day streak</span>
            </div>

            <button
              onClick={() => onLogEntry(habit.id)}
              className="log-btn"
            >
              ✓ Log Today
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HabitList
