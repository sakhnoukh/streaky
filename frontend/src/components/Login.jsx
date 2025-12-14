import { useState } from 'react'

function Login({ onLogin, onRegister, error }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isRegisterMode, setIsRegisterMode] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (isRegisterMode) {
      onRegister(username, password)
    } else {
      onLogin(username, password)
    }
  }

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode)
    setUsername('')
    setPassword('')
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Streaky</h1>
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
              minLength="6"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-btn">
            {isRegisterMode ? 'Register' : 'Login'}
          </button>
        </form>

        <div className="login-toggle">
          <button type="button" onClick={toggleMode} className="toggle-btn">
            {isRegisterMode ? 'Already have an account? Login' : 'Need an account? Register'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Login
