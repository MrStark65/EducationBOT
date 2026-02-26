import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function AnalyticsDashboard({ token }) {
  const [systemAnalytics, setSystemAnalytics] = useState(null);
  const [allUsersAnalytics, setAllUsersAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      // Fetch system analytics
      const systemResponse = await fetch(`${API_URL}/api/admin/analytics/system`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const systemData = await systemResponse.json();
      setSystemAnalytics(systemData);

      // Fetch all users analytics
      const usersResponse = await fetch(`${API_URL}/api/admin/analytics/all-users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const usersData = await usersResponse.json();
      setAllUsersAnalytics(usersData.users || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  // Calculate top performers
  const topPerformers = [...allUsersAnalytics]
    .sort((a, b) => b.completion_rate - a.completion_rate)
    .slice(0, 5);

  // Calculate streak leaders
  const streakLeaders = [...allUsersAnalytics]
    .sort((a, b) => b.current_streak - a.current_streak)
    .slice(0, 5);

  return (
    <div className="analytics-dashboard">
      <div className="page-header">
        <div>
          <h2>📊 Analytics Dashboard</h2>
          <p className="subtitle">System-wide performance metrics and insights</p>
        </div>
        <button className="btn-refresh" onClick={fetchAnalytics}>
          🔄 Refresh
        </button>
      </div>

      {/* System Overview Cards */}
      {systemAnalytics && (
        <div className="stats-grid">
          <div className="stat-card blue">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <div className="stat-value">{systemAnalytics.total_users}</div>
              <div className="stat-label">Total Users</div>
            </div>
          </div>

          <div className="stat-card green">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-value">{systemAnalytics.active_users}</div>
              <div className="stat-label">Active Users (7d)</div>
            </div>
          </div>

          <div className="stat-card purple">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-value">{systemAnalytics.average_completion_rate}%</div>
              <div className="stat-label">Avg Completion Rate</div>
            </div>
          </div>

          <div className="stat-card orange">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <div className="stat-value">{systemAnalytics.total_completions}</div>
              <div className="stat-label">Total Completions</div>
            </div>
          </div>

          <div className="stat-card red">
            <div className="stat-icon">🚫</div>
            <div className="stat-content">
              <div className="stat-value">{systemAnalytics.blocked_users}</div>
              <div className="stat-label">Blocked Users</div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboards */}
      <div className="leaderboards-grid">
        {/* Top Performers */}
        <div className="leaderboard-card">
          <div className="leaderboard-header">
            <h3>🏆 Top Performers</h3>
            <p>Highest completion rates</p>
          </div>
          <div className="leaderboard-list">
            {topPerformers.map((user, index) => (
              <div key={user.chat_id} className="leaderboard-item">
                <div className="rank">{index + 1}</div>
                <div className="user-avatar-small">
                  {user.username?.charAt(0).toUpperCase() || '?'}
                </div>
                <div className="user-details">
                  <div className="username">{user.username || 'Unknown'}</div>
                  <div className="user-meta">
                    {user.completed_days}/{user.total_days} days
                  </div>
                </div>
                <div className="completion-badge">
                  {user.completion_rate}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Streak Leaders */}
        <div className="leaderboard-card">
          <div className="leaderboard-header">
            <h3>🔥 Streak Leaders</h3>
            <p>Longest current streaks</p>
          </div>
          <div className="leaderboard-list">
            {streakLeaders.map((user, index) => (
              <div key={user.chat_id} className="leaderboard-item">
                <div className="rank">{index + 1}</div>
                <div className="user-avatar-small">
                  {user.username?.charAt(0).toUpperCase() || '?'}
                </div>
                <div className="user-details">
                  <div className="username">{user.username || 'Unknown'}</div>
                  <div className="user-meta">
                    Best: {user.longest_streak} days
                  </div>
                </div>
                <div className="streak-badge">
                  🔥 {user.current_streak}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* All Users Table */}
      <div className="users-table-card">
        <div className="table-header">
          <h3>📋 All Users Performance</h3>
          <p>{allUsersAnalytics.length} users registered</p>
        </div>
        <div className="table-container">
          <table className="users-table">
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
                    <div className="table-user">
                      <div className="user-avatar-tiny">
                        {user.username?.charAt(0).toUpperCase() || '?'}
                      </div>
                      <div>
                        <div className="table-username">{user.username || 'Unknown'}</div>
                        <div className="table-chat-id">{user.chat_id}</div>
                      </div>
                    </div>
                  </td>
                  <td>{user.total_days}</td>
                  <td>{user.completed_days}</td>
                  <td>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar-fill" 
                        style={{ width: `${user.completion_rate}%` }}
                      ></div>
                      <span className="progress-text">{user.completion_rate}%</span>
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
                    <span className={`status-badge ${user.is_blocked ? 'blocked' : 'active'}`}>
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
