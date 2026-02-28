import React, { useState, useEffect } from 'react';
import './UserManagement.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function UserManagement({ token }) {
  const [users, setUsers] = useState([]);
  const [blockedUsers, setBlockedUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [blockReason, setBlockReason] = useState('');
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchUsers();
    fetchBlockedUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchBlockedUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/users/blocked`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setBlockedUsers(data.users || []);
    } catch (error) {
      console.error('Error fetching blocked users:', error);
    }
  };

  const fetchUserAnalytics = async (chatId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/admin/users/${chatId}/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUserAnalytics(data);
      setSelectedUser(chatId);
    } catch (error) {
      console.error('Error fetching user analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockUser = async () => {
    if (!selectedUser || !blockReason.trim()) {
      alert('Please provide a reason for blocking');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/admin/users/${selectedUser}/block`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: blockReason })
      });

      if (response.ok) {
        alert('User blocked successfully');
        setShowBlockModal(false);
        setBlockReason('');
        fetchUsers();
        fetchBlockedUsers();
      } else {
        alert('Failed to block user');
      }
    } catch (error) {
      console.error('Error blocking user:', error);
      alert('Error blocking user');
    } finally {
      setLoading(false);
    }
  };

  const handleUnblockUser = async (chatId) => {
    if (!confirm('Are you sure you want to unblock this user?')) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/admin/users/${chatId}/unblock`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('User unblocked successfully');
        fetchUsers();
        fetchBlockedUsers();
      } else {
        alert('Failed to unblock user');
      }
    } catch (error) {
      console.error('Error unblocking user:', error);
      alert('Error unblocking user');
    } finally {
      setLoading(false);
    }
  };

  const openBlockModal = (chatId) => {
    setSelectedUser(chatId);
    setShowBlockModal(true);
  };

  return (
    <div className="user-management">
      <div className="page-header">
        <div>
          <h2>👥 User Management</h2>
          <p className="subtitle">Manage users, view analytics, and control access</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All Users ({users.length})
        </button>
        <button 
          className={`tab ${activeTab === 'blocked' ? 'active' : ''}`}
          onClick={() => setActiveTab('blocked')}
        >
          Blocked Users ({blockedUsers.length})
        </button>
      </div>

      {/* All Users Tab */}
      {activeTab === 'all' && (
        <div className="users-grid">
          {users.map(user => (
            <div key={user.chat_id} className="user-card">
              <div className="user-card-header">
                <div className="user-avatar">
                  {user.username?.charAt(0).toUpperCase() || '?'}
                </div>
                <div className="user-info">
                  <h3>{user.username || 'Unknown'}</h3>
                  <p className="chat-id">{user.chat_id}</p>
                </div>
                <span className="status-badge active">Active</span>
              </div>

              <div className="user-stats">
                <div className="stat">
                  <span className="stat-label">Streak</span>
                  <span className="stat-value">🔥 {user.streak || 0}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Days</span>
                  <span className="stat-value">{user.day_count || 0}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Logs</span>
                  <span className="stat-value">{user.total_logs || 0}</span>
                </div>
              </div>

              <div className="user-actions">
                <button 
                  className="btn-analytics"
                  onClick={() => fetchUserAnalytics(user.chat_id)}
                >
                  📊 Analytics
                </button>
                <button 
                  className="btn-block"
                  onClick={() => openBlockModal(user.chat_id)}
                >
                  🚫 Block
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Blocked Users Tab */}
      {activeTab === 'blocked' && (
        <div className="blocked-users-list">
          {blockedUsers.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✅</div>
              <h3>No Blocked Users</h3>
              <p>All users are currently active</p>
            </div>
          ) : (
            blockedUsers.map(user => (
              <div key={user.chat_id} className="blocked-user-card">
                <div className="blocked-user-info">
                  <div className="user-avatar blocked">
                    {user.username?.charAt(0).toUpperCase() || '?'}
                  </div>
                  <div>
                    <h4>{user.username || 'Unknown'}</h4>
                    <p className="chat-id">{user.chat_id}</p>
                    <p className="block-reason">
                      <strong>Reason:</strong> {user.reason || 'No reason provided'}
                    </p>
                    <p className="block-date">
                      Blocked: {new Date(user.blocked_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <button 
                  className="btn-unblock"
                  onClick={() => handleUnblockUser(user.chat_id)}
                  disabled={loading}
                >
                  ✓ Unblock
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* User Analytics Modal */}
      {userAnalytics && (
        <div className="modal-overlay" onClick={() => setUserAnalytics(null)}>
          <div className="modal analytics-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📊 User Analytics</h3>
              <button className="close-btn" onClick={() => setUserAnalytics(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="analytics-grid">
                <div className="analytics-card">
                  <div className="analytics-icon">📅</div>
                  <div className="analytics-value">{userAnalytics.total_days}</div>
                  <div className="analytics-label">Total Days</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-icon">✅</div>
                  <div className="analytics-value">{userAnalytics.completed_days}</div>
                  <div className="analytics-label">Completed</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-icon">📈</div>
                  <div className="analytics-value">{userAnalytics.completion_rate}%</div>
                  <div className="analytics-label">Completion Rate</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-icon">🔥</div>
                  <div className="analytics-value">{userAnalytics.current_streak}</div>
                  <div className="analytics-label">Current Streak</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-icon">🏆</div>
                  <div className="analytics-value">{userAnalytics.longest_streak}</div>
                  <div className="analytics-label">Longest Streak</div>
                </div>
                <div className="analytics-card">
                  <div className="analytics-icon">⏰</div>
                  <div className="analytics-value">
                    {userAnalytics.last_activity 
                      ? new Date(userAnalytics.last_activity).toLocaleDateString()
                      : 'Never'}
                  </div>
                  <div className="analytics-label">Last Activity</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Block User Modal */}
      {showBlockModal && (
        <div className="modal-overlay" onClick={() => setShowBlockModal(false)}>
          <div className="modal block-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🚫 Block User</h3>
              <button className="close-btn" onClick={() => setShowBlockModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to block this user?</p>
              <div className="form-group">
                <label>Reason for blocking:</label>
                <textarea
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  placeholder="Enter reason (required)"
                  rows="3"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn-cancel"
                onClick={() => setShowBlockModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn-block-confirm"
                onClick={handleBlockUser}
                disabled={loading || !blockReason.trim()}
              >
                {loading ? 'Blocking...' : 'Block User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserManagement;
