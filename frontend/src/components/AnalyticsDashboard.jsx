import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function AnalyticsDashboard({ token }) {
  const [systemAnalytics, setSystemAnalytics] = useState(null);
  const [allUsersAnalytics, setAllUsersAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [systemRes, usersRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/analytics/system`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/admin/analytics/all-users`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      const systemData = await systemRes.json();
      const usersData = await usersRes.json();

      setSystemAnalytics(systemData);
      setAllUsersAnalytics(usersData.users || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-content">
        <div className="loading-spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  const topPerformers = [...allUsersAnalytics]
    .sort((a, b) => b.completion_rate - a.completion_rate)
    .slice(0, 5);

  const streakLeaders = [...allUsersAnalytics]
    .sort((a, b) => b.current_streak - a.current_streak)
    .slice(0, 5);

  return (
    <div className="analytics-dashboard">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1>📊 Analytics Dashboard</h1>
          <p>System-wide performance metrics and insights</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchAnalytics}>
          <span>🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Grid */}
      {systemAnalytics && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon primary">👥</div>
            <div className="stat-content">
              <h3>{systemAnalytics.total_users}</h3>
              <p>Total Users</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon success">✅</div>
            <div className="stat-content">
              <h3>{systemAnalytics.active_users}</h3>
              <p>Active Users (7d)</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon warning">📈</div>
            <div className="stat-content">
              <h3>{systemAnalytics.average_completion_rate}%</h3>
              <p>Avg Completion Rate</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon danger">🎯</div>
            <div className="stat-content">
              <h3>{systemAnalytics.total_completions}</h3>
              <p>Total Completions</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{background: 'var(--gray-100)'}}>🚫</div>
            <div className="stat-content">
              <h3>{systemAnalytics.blocked_users}</h3>
              <p>Blocked Users</p>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboards */}
      <div className="leaderboards-grid">
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">🏆 Top Performers</h3>
              <p style={{margin: '4px 0 0 0', fontSize: '13px', color: 'var(--gray-500)'}}>
                Highest completion rates
              </p>
            </div>
          </div>
          <div className="leaderboard-list">
            {topPerformers.map((user, index) => (
              <div key={user.chat_id} className="leaderboard-item">
                <div className="rank-badge">{index + 1}</div>
                <div className="user-avatar">{user.username?.charAt(0).toUpperCase() || '?'}</div>
                <div className="user-info">
                  <span className="user-name">{user.username || 'Unknown'}</span>
                  <span className="user-meta">{user.completed_days}/{user.total_days} days</span>
                </div>
                <span className="badge badge-success">{user.completion_rate}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">🔥 Streak Leaders</h3>
              <p style={{margin: '4px 0 0 0', fontSize: '13px', color: 'var(--gray-500)'}}>
                Longest current streaks
              </p>
            </div>
          </div>
          <div className="leaderboard-list">
            {streakLeaders.map((user, index) => (
              <div key={user.chat_id} className="leaderboard-item">
                <div className="rank-badge">{index + 1}</div>
                <div className="user-avatar">{user.username?.charAt(0).toUpperCase() || '?'}</div>
                <div className="user-info">
                  <span className="user-name">{user.username || 'Unknown'}</span>
                  <span className="user-meta">Best: {user.longest_streak} days</span>
                </div>
                <span className="badge badge-warning">🔥 {user.current_streak}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">📋 All Users Performance</h3>
            <p style={{margin: '4px 0 0 0', fontSize: '13px', color: 'var(--gray-500)'}}>
              {allUsersAnalytics.length} users registered
            </p>
          </div>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Total Days</th>
                <th>Completed</th>
                <th>Completion Rate</th>
                <th>Current Streak</th>
                <th>Best Streak</th>
                <th>Last Activity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {allUsersAnalytics.map(user => (
                <tr key={user.chat_id}>
                  <td>
                    <div className="user-cell">
                      <div className="user-avatar">{user.username?.charAt(0).toUpperCase() || '?'}</div>
                      <div>
                        <div className="user-name">{user.username || 'Unknown'}</div>
                        <div className="user-meta">{user.chat_id}</div>
                      </div>
                    </div>
                  </td>
                  <td>{user.total_days}</td>
                  <td>{user.completed_days}</td>
                  <td>
                    <div className="progress-cell">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${user.completion_rate}%` }}
                        ></div>
                      </div>
                      <span>{user.completion_rate}%</span>
                    </div>
                  </td>
                  <td>
                    <span className="streak-value">🔥 {user.current_streak}</span>
                  </td>
                  <td>{user.longest_streak}</td>
                  <td>
                    {user.last_activity 
                      ? new Date(user.last_activity).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td>
                    <span className={`badge ${user.is_blocked ? 'badge-danger' : 'badge-success'}`}>
                      {user.is_blocked ? 'Blocked' : 'Active'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;