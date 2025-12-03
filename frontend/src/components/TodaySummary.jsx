import './TodaySummary.css'

function TodaySummary({ habits }) {
  // Calculate summary stats from habits
  const totalHabits = habits.length
  
  // For "completed today" we'd need to track this - for now we'll show habits with active streaks
  // A streak > 0 means they've been logging recently
  const activeStreaks = habits.filter(h => h.streak > 0).length
  
  // Find the longest current streak
  const longestStreak = habits.reduce((max, h) => Math.max(max, h.streak), 0)
  
  // Find the best streak ever
  const bestEver = habits.reduce((max, h) => Math.max(max, h.best_streak), 0)

  if (totalHabits === 0) {
    return null // Don't show summary if no habits
  }

  return (
    <div className="today-summary">
      <div className="summary-greeting">
        <h2>👋 Welcome back!</h2>
        <p className="summary-date">{new Date().toLocaleDateString('en-US', { 
          weekday: 'long', 
          month: 'long', 
          day: 'numeric' 
        })}</p>
      </div>
      
      <div className="summary-stats">
        <div className="summary-stat">
          <span className="summary-stat-number">{totalHabits}</span>
          <span className="summary-stat-label">Total Habits</span>
        </div>
        
        <div className="summary-stat">
          <span className="summary-stat-number">{activeStreaks}</span>
          <span className="summary-stat-label">Active Streaks</span>
        </div>
        
        <div className="summary-stat highlight">
          <span className="summary-stat-number">🔥 {longestStreak}</span>
          <span className="summary-stat-label">Longest Streak</span>
        </div>
        
        <div className="summary-stat">
          <span className="summary-stat-number">⭐ {bestEver}</span>
          <span className="summary-stat-label">Best Ever</span>
        </div>
      </div>
    </div>
  )
}

export default TodaySummary
