import { useState, useEffect } from 'react'
// Import shared styles FIRST (before App.css)
import './styles/variables.css'
import './styles/layout.css'
import './styles/components.css'
import './App.css'

import Login from './components/Login'
import ScheduleConfig from './components/ScheduleConfig'
import ScheduleSummary from './components/ScheduleSummary'
import PlaylistManager from './components/PlaylistManager'
import PlaylistStatus from './components/PlaylistStatus'
import BroadcastMessage from './components/BroadcastMessage'
import FileLibrary from './components/FileLibrary'
import UserManagement from './components/UserManagement'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import DatabaseViewer from './components/DatabaseViewer'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authToken, setAuthToken] = useState(null)
  const [checkingAuth, setCheckingAuth] = useState(true)

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

  if (checkingAuth) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Checking authentication...</p>
      </div>
    )
  }

  // Return ONLY Login component when not authenticated - no wrapper divs!
  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return <DashboardLayout authToken={authToken} onLogout={handleLogout} />
}

function DashboardLayout({ authToken, onLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 1024)
  const [activeMenu, setActiveMenu] = useState('dashboard')
  const [allUsers, setAllUsers] = useState([])
  const [systemStats, setSystemStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Close sidebar on mobile when clicking outside
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 1024) {
        setSidebarOpen(true)
      } else {
        setSidebarOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const fetchAllUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      })
      if (res.ok) {
        const data = await res.json()
        setAllUsers(data.users || [])
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const fetchSystemStats = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/system/stats`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      })
      if (res.ok) {
        const data = await res.json()
        setSystemStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGlobalReset = async () => {
    if (!confirm('⚠️ Reset Global Progress?\n\nThis affects ALL users. Are you sure?')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/reset-global`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
      })

      if (response.ok) {
        alert('✅ Global progress reset successfully!')
        fetchAllUsers()
        fetchSystemStats()
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
    fetchSystemStats()
    const interval = setInterval(() => {
      fetchAllUsers()
      fetchSystemStats()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard', badge: null },
    { id: 'analytics', icon: '📈', label: 'Analytics', badge: null },
    { id: 'schedule', icon: '⏰', label: 'Schedule', badge: null },
    { id: 'playlists', icon: '📚', label: 'Playlists', badge: null },
    { id: 'broadcast', icon: '📢', label: 'Broadcast', badge: null },
    { id: 'users', icon: '👥', label: 'Users', badge: allUsers.length },
    { id: 'user-management', icon: '🛡️', label: 'User Management', badge: null },
    { id: 'database', icon: '🗄️', label: 'Database', badge: null },
    { id: 'system', icon: '⚙️', label: 'System', badge: systemStats?.errors?.recent || null },
  ]

  const handleMenuClick = (menuId) => {
    setActiveMenu(menuId)
    // Close sidebar on mobile after menu click
    if (window.innerWidth <= 1024) {
      setSidebarOpen(false)
    }
  }

  const handleOverlayClick = () => {
    if (window.innerWidth <= 1024) {
      setSidebarOpen(false)
    }
  }

  return (
    <div className="dastone-layout">
      {/* Mobile Overlay */}
      {sidebarOpen && window.innerWidth <= 1024 && (
        <div className="sidebar-overlay" onClick={handleOverlayClick}></div>
      )}
      
      {/* Sidebar */}
      <aside className={`dastone-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-icon">🎖️</span>
            {sidebarOpen && (
              <div className="logo-text">
                <h1>Officer Priya</h1>
                <p>CDS System</p>
              </div>
            )}
          </div>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activeMenu === item.id ? 'active' : ''}`}
              onClick={() => handleMenuClick(item.id)}
              title={item.label}
            >
              <span className="nav-icon">{item.icon}</span>
              {sidebarOpen && (
                <>
                  <span className="nav-label">{item.label}</span>
                  {item.badge && <span className="nav-badge">{item.badge}</span>}
                </>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item" onClick={onLogout} title="Logout">
            <span className="nav-icon">🚪</span>
            {sidebarOpen && <span className="nav-label">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="dastone-main">
        {/* Top Bar */}
        <header className="dastone-topbar">
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <span className="toggle-icon">{sidebarOpen ? '◀' : '▶'}</span>
          </button>

          <div className="topbar-title">
            <h2>{menuItems.find(m => m.id === activeMenu)?.label || 'Dashboard'}</h2>
            <p className="breadcrumb">Home / {menuItems.find(m => m.id === activeMenu)?.label}</p>
          </div>

          <div className="topbar-actions">
            <div className="global-badge">
              <span className="badge-icon">🌍</span>
              <span className="badge-text">Global Mode</span>
            </div>
            <button className="btn-icon" onClick={handleGlobalReset} title="Reset Global">
              🔄
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="dastone-content">
          {activeMenu === 'dashboard' && (
            <DashboardView 
              users={allUsers} 
              stats={systemStats} 
              loading={loading}
              authToken={authToken}
            />
          )}
          {activeMenu === 'analytics' && (
            <AnalyticsDashboard token={authToken} />
          )}
          {activeMenu === 'schedule' && (
            <ScheduleView authToken={authToken} />
          )}
          {activeMenu === 'playlists' && (
            <PlaylistsView authToken={authToken} />
          )}
          {activeMenu === 'broadcast' && (
            <BroadcastView authToken={authToken} />
          )}
          {activeMenu === 'users' && (
            <UsersView users={allUsers} loading={loading} />
          )}
          {activeMenu === 'user-management' && (
            <UserManagement token={authToken} />
          )}
          {activeMenu === 'database' && (
            <DatabaseViewer token={authToken} />
          )}
          {activeMenu === 'system' && (
            <SystemView stats={systemStats} authToken={authToken} />
          )}
        </main>
      </div>
    </div>
  )
}

// Dashboard View
function DashboardView({ users, stats, loading, authToken }) {
  if (loading) {
    return <div className="loading-content"><div className="spinner"></div></div>
  }

  return (
    <div className="dashboard-view">
      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats?.users?.total || 0}</h3>
            <p>Total Users</p>
            <span className="stat-change">+{stats?.users?.active || 0} active</span>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{stats?.users?.active || 0}</h3>
            <p>Active Users</p>
            <span className="stat-change">Last 24h</span>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>{stats?.errors?.recent || 0}</h3>
            <p>Recent Errors</p>
            <span className="stat-change">Last 100 logs</span>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">💾</div>
          <div className="stat-content">
            <h3>{stats?.backups?.total || 0}</h3>
            <p>Backups</p>
            <span className="stat-change">Auto-managed</span>
          </div>
        </div>
      </div>

      {/* Recent Users */}
      <div className="dashboard-section">
        <div className="section-header">
          <h3>Recent Users</h3>
          <span className="section-badge">{users.length} total</span>
        </div>
        <div className="users-table">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Streak</th>
                <th>Progress</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.slice(0, 5).map(user => (
                <tr key={user.id}>
                  <td>
                    <div className="user-cell">
                      <div className="user-avatar">{user.first_name?.charAt(0)}</div>
                      <div>
                        <div className="user-name">{user.first_name} {user.last_name}</div>
                        <div className="user-username">@{user.username || 'N/A'}</div>
                      </div>
                    </div>
                  </td>
                  <td><span className="badge badge-fire">🔥 {user.streak}</span></td>
                  <td><span className="badge badge-info">📝 {user.total_logs}</span></td>
                  <td>
                    <span className={`status-dot ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// Schedule View
function ScheduleView({ authToken }) {
  const [activeTab, setActiveTab] = useState('summary')
  
  return (
    <div className="content-view">
      <div className="view-header">
        <h3>Schedule Management</h3>
        <p>View and configure content delivery schedule</p>
      </div>
      
      <div className="schedule-tabs">
        <button 
          className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          📊 Schedule Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'config' ? 'active' : ''}`}
          onClick={() => setActiveTab('config')}
        >
          ⚙️ Schedule Config
        </button>
      </div>
      
      {activeTab === 'summary' && <ScheduleSummary token={authToken} />}
      {activeTab === 'config' && <ScheduleConfig chatId={null} authToken={authToken} />}
    </div>
  )
}

// Playlists View
function PlaylistsView({ authToken }) {
  const [activeTab, setActiveTab] = useState('manager')
  
  return (
    <div className="content-view">
      <div className="view-header">
        <h3>Playlist Management</h3>
        <p>Manage YouTube playlists and scheduling</p>
      </div>
      
      <div className="schedule-tabs">
        <button 
          className={`tab-button ${activeTab === 'manager' ? 'active' : ''}`}
          onClick={() => setActiveTab('manager')}
        >
          📚 Playlists & Schedule
        </button>
        <button 
          className={`tab-button ${activeTab === 'status' ? 'active' : ''}`}
          onClick={() => setActiveTab('status')}
        >
          📊 Progress & Status
        </button>
      </div>
      
      {activeTab === 'manager' && <PlaylistManager chatId={null} authToken={authToken} />}
      {activeTab === 'status' && <PlaylistStatus token={authToken} />}
    </div>
  )
}

// Files View
function FilesView({ authToken }) {
  console.log('FilesView rendered with authToken:', authToken ? 'present' : 'MISSING');
  
  if (!authToken) {
    return (
      <div className="content-view">
        <div className="loading-content">
          <div className="spinner"></div>
          <p>Authenticating...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="content-view">
      <div className="view-header">
        <h3>File Library</h3>
        <p>Upload and manage study materials</p>
      </div>
      <FileLibrary chatId={null} authToken={authToken} />
    </div>
  )
}

// Users View
function UsersView({ users, loading }) {
  if (loading) {
    return <div className="loading-content"><div className="spinner"></div></div>
  }

  return (
    <div className="content-view">
      <div className="view-header">
        <h3>Registered Users</h3>
        <p>{users.length} users registered</p>
      </div>

      <div className="users-grid-view">
        {users.map(user => (
          <div key={user.id} className="user-card-modern">
            <div className="user-card-header">
              <div className="user-avatar-large">{user.first_name?.charAt(0)}</div>
              <span className={`status-indicator ${user.is_active ? 'active' : 'inactive'}`}></span>
            </div>
            <div className="user-card-body">
              <h4>{user.first_name} {user.last_name}</h4>
              <p className="user-username">@{user.username || 'N/A'}</p>
              <p className="user-id">ID: {user.chat_id}</p>
            </div>
            <div className="user-card-stats">
              <div className="stat-item">
                <span className="stat-icon">🔥</span>
                <span className="stat-value">{user.streak}</span>
                <span className="stat-label">Streak</span>
              </div>
              <div className="stat-item">
                <span className="stat-icon">📝</span>
                <span className="stat-value">{user.total_logs}</span>
                <span className="stat-label">Logs</span>
              </div>
              <div className="stat-item">
                <span className="stat-icon">📅</span>
                <span className="stat-value">{user.day_count}</span>
                <span className="stat-label">Days</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Broadcast View
function BroadcastView({ authToken }) {
  return (
    <div className="content-view">
      <BroadcastMessage token={authToken} />
    </div>
  )
}

// System View
function SystemView({ stats, authToken }) {
  const [clearing, setClearing] = useState(false);
  const [message, setMessage] = useState('');

  const handleClearErrors = async () => {
    if (!confirm('Clear all system errors? This will remove error logs older than 30 days.')) {
      return;
    }

    setClearing(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/system/errors?days=0`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`✅ Cleared ${data.deleted} error(s)`);
        setTimeout(() => window.location.reload(), 1500);
      } else {
        setMessage('❌ Failed to clear errors');
      }
    } catch (err) {
      setMessage('❌ Error clearing logs');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="content-view">
      <div className="view-header">
        <h3>System Information</h3>
        <p>Monitor system health and performance</p>
      </div>

      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      <div className="system-info-grid">
        <div className="info-card">
          <h4>System Version</h4>
          <p className="info-value">{stats?.system?.version || '2.0.0'}</p>
        </div>
        <div className="info-card">
          <h4>Total Errors</h4>
          <p className="info-value">
            {stats?.errors?.total || 0}
            {stats?.errors?.total > 0 && (
              <button 
                onClick={handleClearErrors}
                disabled={clearing}
                className="btn-clear-errors"
                style={{ marginLeft: '10px', fontSize: '12px', padding: '4px 8px' }}
              >
                {clearing ? 'Clearing...' : '🗑️ Clear'}
              </button>
            )}
          </p>
        </div>
        <div className="info-card">
          <h4>Latest Backup</h4>
          <p className="info-value">
            {stats?.backups?.latest?.created ? 
              new Date(stats.backups.latest.created).toLocaleString() : 
              'No backups'}
          </p>
        </div>
        <div className="info-card">
          <h4>Uptime</h4>
          <p className="info-value">{stats?.system?.uptime || 'N/A'}</p>
        </div>
      </div>
    </div>
  )
}

export default App