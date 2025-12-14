import CategoryBadge from './CategoryBadge'

function HabitList({ habits, onLogEntry, onEdit, onDelete, onViewCalendar, onManageCategories, onViewJournal }) {
  if (habits.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🚀</div>
        <h3>Start Your Journey</h3>
        <p>Create your first habit and begin building streaks that stick!</p>
        <div className="empty-state-tips">
          <span>💡 Tip: Start small with just one habit</span>
        </div>
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
                  onClick={() => onManageCategories(habit)}
                  className="action-btn category-btn"
                  title="Manage categories"
                >
                  🏷️
                </button>
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
            
            <div className="habit-badges">
              <span className="goal-badge">{habit.goal_type}</span>
              {habit.categories && habit.categories.map((cat) => (
                <CategoryBadge key={cat.id} category={cat} small />
              ))}
            </div>
            
            {habit.reminder_time && (
              <div className="reminder-badge" title={`Reminder set for ${habit.reminder_time}`}>
                ⏰ {habit.reminder_time}
              </div>
            )}
            
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
            
            {habit.streak >= 7 && (
              <div className="streak-badge">
                {habit.streak >= 30 ? '🏆 30+ Day Champion!' : 
                 habit.streak >= 14 ? '💪 2 Week Warrior!' : 
                 '🌟 Week Streak!'}
              </div>
            )}

            <div className="habit-actions-bottom">
              <button
                onClick={() => onViewCalendar(habit)}
                className="calendar-btn"
                title="View calendar"
              >
                📅 Calendar
              </button>
              <button
                onClick={() => onViewJournal(habit)}
                className="journal-btn"
                title="View journal entries"
              >
                📝 Journal
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
