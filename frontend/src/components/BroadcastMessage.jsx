import { useState, useEffect } from 'react'
import './BroadcastMessage.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function BroadcastMessage({ token }) {
  const [message, setMessage] = useState('')
  const [target, setTarget] = useState('all')
  const [selectedUser, setSelectedUser] = useState('')
  const [users, setUsers] = useState([])
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data.users || [])
      }
    } catch (err) {
      console.error('Error fetching users:', err)
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()

    if (!message.trim()) {
      setError('Please enter a message')
      return
    }

    if (target === 'specific' && !selectedUser) {
      setError('Please select a user')
      return
    }

    try {
      setSending(true)
      setError(null)
      setResult(null)

      const response = await fetch(`${API_BASE_URL}/api/admin/broadcast`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          target: target,
          chat_id: target === 'specific' ? selectedUser : null
        })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to send message')
      }

      const data = await response.json()
      setResult(data)
      setMessage('')
      
      // Clear result after 5 seconds
      setTimeout(() => setResult(null), 5000)
    } catch (err) {
      console.error('Error sending broadcast:', err)
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  const activeUsers = users.filter(u => u.is_active)

  return (
    <div className="broadcast-container">
      <div className="broadcast-header">
        <h2>📢 Broadcast Message</h2>
        <p>Send announcements or messages to your users</p>
      </div>

      {result && (
        <div className="success-banner">
          ✅ {result.message}
          {result.sent_count && (
            <div className="broadcast-stats">
              Sent: {result.sent_count} | Failed: {result.failed_count || 0}
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error-banner">
          ❌ {error}
        </div>
      )}

      <form onSubmit={handleSend} className="broadcast-form">
        <div className="form-section">
          <label className="form-label">Target Audience</label>
          <div className="target-selector">
            <label className="radio-option">
              <input
                type="radio"
                value="all"
                checked={target === 'all'}
                onChange={(e) => setTarget(e.target.value)}
              />
              <span className="radio-label">
                <span className="radio-icon">📣</span>
                <span className="radio-text">
                  <strong>All Users</strong>
                  <small>{activeUsers.length} active users</small>
                </span>
              </span>
            </label>

            <label className="radio-option">
              <input
                type="radio"
                value="specific"
                checked={target === 'specific'}
                onChange={(e) => setTarget(e.target.value)}
              />
              <span className="radio-label">
                <span className="radio-icon">👤</span>
                <span className="radio-text">
                  <strong>Specific User</strong>
                  <small>Send to one person</small>
                </span>
              </span>
            </label>
          </div>
        </div>

        {target === 'specific' && (
          <div className="form-section">
            <label className="form-label">Select User</label>
            <select
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
              className="user-select"
              required
            >
              <option value="">Choose a user...</option>
              {activeUsers.map(user => (
                <option key={user.chat_id} value={user.chat_id}>
                  {user.first_name} {user.last_name} (@{user.username || 'N/A'})
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="form-section">
          <label className="form-label">Message</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message here... (e.g., 'Tomorrow's schedule has been updated. Check /schedule for details.')"
            className="message-textarea"
            rows="6"
            required
          />
          <div className="char-count">
            {message.length} characters
          </div>
        </div>

        <div className="form-section preview-section">
          <label className="form-label">Preview</label>
          <div className="message-preview">
            <div className="preview-header">
              {target === 'all' ? '📢 ANNOUNCEMENT' : '📬 MESSAGE FROM ADMIN'}
            </div>
            <div className="preview-body">
              {message || 'Your message will appear here...'}
            </div>
            <div className="preview-footer">
              — Admin Team
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={() => {
              setMessage('')
              setSelectedUser('')
              setError(null)
              setResult(null)
            }}
            className="btn-secondary"
            disabled={sending}
          >
            Clear
          </button>
          <button
            type="submit"
            className="btn-send"
            disabled={sending || !message.trim()}
          >
            {sending ? (
              <>⏳ Sending...</>
            ) : (
              <>📤 Send {target === 'all' ? `to ${activeUsers.length} users` : 'Message'}</>
            )}
          </button>
        </div>
      </form>

      <div className="broadcast-tips">
        <h3>💡 Tips for Effective Messages</h3>
        <ul>
          <li>Keep messages clear and concise</li>
          <li>Use emojis to make messages more engaging</li>
          <li>Include action items or next steps</li>
          <li>Test with a specific user before broadcasting to all</li>
          <li>Avoid sending too many broadcasts (respect user attention)</li>
        </ul>
      </div>
    </div>
  )
}

export default BroadcastMessage
