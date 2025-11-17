import { useState } from 'react'

function Login({ onLogin, error }) {
  const [username, setUsername] = useState('testuser')
  const [password, setPassword] = useState('testpass')

  const handleSubmit = (e) => {
    e.preventDefault()
    onLogin(username, password)
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>🎯 Streaky</h1>
        <h2>Habit Tracker</h2>
        <p className="login-subtitle">Track your habits, build your streaks</p>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-btn">
            Login
          </button>
        </form>

        <div className="login-hint">
          <small>Dev credentials: testuser / testpass</small>
        </div>
      </div>
    </div>
  )
}

export default Login
