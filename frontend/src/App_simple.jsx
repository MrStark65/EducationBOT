import { useState, useEffect } from 'react'
import './App.css'
import Login from './components/Login'
import ScheduleConfig from './components/ScheduleConfig'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authToken, setAuthToken] = useState(null)
  const [checkingAuth, setCheckingAuth] = useState(true)

  // Check authentication on mount - MUST be before any conditional returns
  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    const expires = localStorage.getItem('token_expires')
    
    if (token && expires && Date.now() < parseInt(expires)) {
      verifyToken(token)
    } else {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('token_expires')
      setCheckingAuth(false)
    }
  }, [])

  const verifyToken = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        setAuthToken(token)
        setIsAuthenticated(true)
      } else {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('token_expires')
      }
    } catch (error) {
      console.error('Token verification failed:', error)
      localStorage.removeItem('auth_token')
      localStorage.removeItem('token_expires')
    } finally {
      setCheckingAuth(false)
    }
  }

  const handleLoginSuccess = (token) => {
    setAuthToken(token)
    setIsAuthenticated(true)
    setCheckingAuth(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('token_expires')
    setAuthToken(null)
    setIsAuthenticated(false)
  }

  // Show loading while checking auth
  if (checkingAuth) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        🔐 Checking authentication...
      </div>
    )
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  // Main authenticated app
  return <AuthenticatedApp authToken={authToken} onLogout={handleLogout} />
}

// Separate component for the authenticated app
function AuthenticatedApp({ authToken, onLogout }) {
  const [allUsers, setAllUsers] = useState([])
  const [activeTab, setActiveTab] = useState('schedule')
  const [loading, setLoading] = useState(true)

  const fetchAllUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      if (res.ok) {
        const data = await res.json()
        setAllUsers(data.users || [])
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGlobalReset = async () => {
    if (!confirm('⚠️ Reset Global Progress?\n\nThis will:\n- Reset global day counter to 0\n- Reset all playlist indices to 0\n- Clear all user logs\n\nThis affects ALL users. Are you sure?')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/reset-global`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        alert('✅ Global progress reset successfully!')
        fetchAllUsers()
      } else {
        const data = await response.json()
        alert(`❌ ${data.detail || 'Failed to reset'}`)
      }
    } catch (error) {
      console.error('Error resetting:', error)
      alert('❌ Failed to reset global progress')
    }
  }

  useEffect(() => {
    fetchAllUsers()
    const userInterval = setInterval(fetchAllUsers, 30000)
    return () => clearInterval(userInterval)
  }, [])

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <p>Loading Officer Priya System...</p>
      </div>
    )
  }

  // Show empty state if no users registered
  if (allUsers.length === 0) {
    return (
      <div className="app">
        <header className="header">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">🎖️</span>
              <div className="logo-text">
                <h1>Officer Priya</h1>
                <p>CDS Preparation System</p>
              </div>
            </div>
            <button className="btn-logout" onClick={onLogout}>
              🚪 Logout
            </button>
          </div>
        </header>

        <main className="main-content">
          <div className="empty-state">
            <div className="empty-icon">👥</div>
            <h2>No Users Registered Yet</h2>
            <p>To get started, send <strong>/start</strong> to @OfficerPriyaBot on Telegram</p>
            <div className="empty-steps">
              <div className="step">
                <span className="step-number">1</span>
                <span className="step-text">Open Telegram</span>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <span className="step-text">Search for @OfficerPriyaBot</span>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <span className="step-text">Send /start command</span>
              </div>
              <div className="step">
                <span className="step-number">4</span>
                <span className="step-text">Refresh this page</span>
              </div>
            </div>
            <button onClick={fetchAllUsers} className="refresh-button">
              🔄 Refresh
            </button>
          </div>
        </main>

        <footer className="footer">
          <p>Built with ❤️ for CDS OTA Preparation</p>
        </footer>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🎖️</span>
            <div className="logo-text">
              <h1>Officer Priya</h1>
              <p>CDS Preparation System</p>
            </div>
          </div>
          <div className="header-stats">
            <div className="global-mode-badge">
              <span className="global-icon">🌍</span>
              <div className="global-info">
                <span className="global-label">Global Mode</span>
                <span className="global-desc">All users receive same content</span>
              </div>
            </div>
            <div className="stat-badge">
              <span className="stat-label">Total Users</span>
              <span className="stat-value">{allUsers.length}</span>
            </div>
            <button className="btn-logout" onClick={onLogout} title="Logout">
              🚪 Logout
            </button>
            <button className="btn-reset-global" onClick={handleGlobalReset} title="Reset global progress">
              🔄 Reset
            </button>
          </div>
        </div>
      </header>

      <nav className="nav-tabs">
        <button 
          className={`nav-tab ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          <span className="tab-icon">⏰</span>
          <span className="tab-label">Global Schedule</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <span className="tab-icon">👥</span>
          <span className="tab-label">Users</span>
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'schedule' && (
          <div className="tab-content">
            <div className="global-notice">
              <span className="notice-icon">ℹ️</span>
              <div className="notice-text">
                <strong>Global Mode:</strong> All settings apply to ALL users. Everyone receives the same content on the same day.
              </div>
            </div>
            <ScheduleConfig chatId={null} authToken={authToken} />
          </div>
        )}

        {activeTab === 'users' && (
          <div className="tab-content">
            <div className="users-section">
              <h2>📊 Registered Users ({allUsers.length})</h2>
              <div className="users-grid">
                {allUsers.map((user) => (
                  <div key={user.id} className="user-card">
                    <div className="user-card-avatar">
                      {user.first_name?.charAt(0) || '?'}
                    </div>
                    <div className="user-card-info">
                      <h3>{user.first_name} {user.last_name}</h3>
                      {user.username && <p className="user-card-username">@{user.username}</p>}
                      <p className="user-card-id">ID: {user.chat_id}</p>
                      <div className="user-card-stats">
                        <span>🔥 Streak: {user.streak}</span>
                        <span>📝 Logs: {user.total_logs}</span>
                        <span>📅 Day: {user.day_count}</span>
                      </div>
                      <div className="user-card-status">
                        <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                          {user.is_active ? '✅ Active' : '⏸️ Inactive'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Built with ❤️ for CDS OTA Preparation</p>
      </footer>
    </div>
  )
}

export default App
