import { useState, useEffect } from 'react'
import './App.css'
import MetricsPanel from './components/MetricsPanel'
import LogsTable from './components/LogsTable'
import ConfigPanel from './components/ConfigPanel'
import AdminActions from './components/AdminActions'
import ScheduleConfig from './components/ScheduleConfig'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [metrics, setMetrics] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [chatId, setChatId] = useState(localStorage.getItem('chatId') || '')
  const [allUsers, setAllUsers] = useState([])
  const [showUserList, setShowUserList] = useState(false)

  const fetchData = async () => {
    if (!chatId) return
    
    try {
      const metricsRes = await fetch(`${API_BASE_URL}/api/dashboard/metrics?chat_id=${chatId}`)
      if (!metricsRes.ok) {
        if (metricsRes.status === 404) {
          setLoginError('User not found. Please send /start to the bot first.')
          setIsLoggedIn(false)
          localStorage.removeItem('chatId')
        }
        console.error('Failed to fetch metrics:', metricsRes.status)
        setLoading(false)
        return
      }
      const metricsData = await metricsRes.json()
      setMetrics(metricsData)

      const logsRes = await fetch(`${API_BASE_URL}/api/dashboard/logs?chat_id=${chatId}&limit=50`)
      if (!logsRes.ok) {
        console.error('Failed to fetch logs:', logsRes.status)
        setLoading(false)
        return
      }
      const logsData = await logsRes.json()
      setLogs(logsData.logs || [])

      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const fetchAllUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/users`)
      if (res.ok) {
        const data = await res.json()
        setAllUsers(data.users || [])
        
        // Auto-select first user if none selected
        if (!chatId && data.users.length > 0) {
          const firstUser = data.users[0]
          setChatId(firstUser.chat_id)
          localStorage.setItem('chatId', firstUser.chat_id)
        }
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const handleUserSwitch = (newChatId) => {
    setChatId(newChatId)
    localStorage.setItem('chatId', newChatId)
    setShowUserList(false)
    setLoading(true)
    fetchData()
  }

  useEffect(() => {
    // Fetch users first
    fetchAllUsers()
    const userInterval = setInterval(fetchAllUsers, 30000) // Refresh users every 30s
    
    return () => {
      clearInterval(userInterval)
    }
  }, [])

  useEffect(() => {
    if (chatId) {
      fetchData()
      const interval = setInterval(fetchData, 5000)
      return () => clearInterval(interval)
    }
  }, [chatId])

  if (loading && chatId) {
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
            <div className="current-user" onClick={() => setShowUserList(!showUserList)}>
              <span className="user-icon">👤</span>
              <div className="user-info">
                <span className="user-name">{metrics?.user_name || 'User'}</span>
                <span className="user-id">ID: {chatId}</span>
              </div>
              <span className="dropdown-icon">{showUserList ? '▲' : '▼'}</span>
            </div>
            <div className="stat-badge">
              <span className="stat-label">Day</span>
              <span className="stat-value">{metrics?.current_day || 0}</span>
            </div>
            <div className="stat-badge streak">
              <span className="stat-icon">🔥</span>
              <span className="stat-value">{metrics?.streak || 0}</span>
            </div>

          </div>
        </div>
        
        {showUserList && (
          <div className="user-dropdown">
            <div className="user-dropdown-header">
              <h3>All Users ({allUsers.length})</h3>
              <button onClick={() => setShowUserList(false)} className="close-dropdown">✕</button>
            </div>
            <div className="user-list">
              {allUsers.map((user) => (
                <div
                  key={user.id}
                  className={`user-item ${user.chat_id === chatId ? 'active' : ''}`}
                  onClick={() => handleUserSwitch(user.chat_id)}
                >
                  <div className="user-item-avatar">
                    {user.first_name?.charAt(0) || '?'}
                  </div>
                  <div className="user-item-info">
                    <div className="user-item-name">
                      {user.first_name} {user.last_name}
                      {user.username && <span className="user-item-username">@{user.username}</span>}
                    </div>
                    <div className="user-item-stats">
                      <span>Day {user.day_count}</span>
                      <span>•</span>
                      <span>🔥 {user.streak}</span>
                      <span>•</span>
                      <span>{user.total_logs} logs</span>
                    </div>
                  </div>
                  {user.chat_id === chatId && (
                    <span className="user-item-badge">Current</span>
                  )}
                </div>
              ))}
              {allUsers.length === 0 && (
                <div className="no-users">
                  <p>No users registered yet</p>
                  <small>Send /start to @OfficerPriyaBot to register</small>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      <nav className="nav-tabs">
        <button 
          className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <span className="tab-icon">📊</span>
          <span className="tab-label">Dashboard</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          <span className="tab-icon">⏰</span>
          <span className="tab-label">Schedule</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'config' ? 'active' : ''}`}
          onClick={() => setActiveTab('config')}
        >
          <span className="tab-icon">⚙️</span>
          <span className="tab-label">Settings</span>
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <>
            <MetricsPanel metrics={metrics} />
            <AdminActions onAction={fetchData} chatId={chatId} />
            <LogsTable logs={logs} />
          </>
        )}
        
        {activeTab === 'schedule' && (
          <ScheduleConfig onUpdate={fetchData} chatId={chatId} />
        )}
        
        {activeTab === 'config' && (
          <ConfigPanel onUpdate={fetchData} chatId={chatId} />
        )}
      </main>

      <footer className="footer">
        <p>Built with ❤️ for CDS OTA Preparation</p>
      </footer>
    </div>
  )
}

export default App
