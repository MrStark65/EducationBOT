import { useState, useEffect } from 'react'
import './ScheduleConfig.css'
import PlaylistManager from './PlaylistManager'
import FileLibrary from './FileLibrary'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function ScheduleConfig({ onUpdate, chatId, authToken }) {
  const [enabled, setEnabled] = useState(false)
  const [time, setTime] = useState('06:00')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [activeSection, setActiveSection] = useState('simple')

  useEffect(() => {
    fetchSchedule()
  }, [])

  const fetchSchedule = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/config/schedule`)
      if (res.ok) {
        const data = await res.json()
        setEnabled(data.enabled)
        setTime(data.time)
      }
    } catch (err) {
      console.error('Error fetching schedule:', err)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    setMessage('')

    try {
      const res = await fetch(`${API_BASE_URL}/api/config/schedule`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, time })
      })

      if (res.ok) {
        setMessage('✅ Global schedule updated successfully!')
        if (onUpdate) onUpdate()
      } else {
        const data = await res.json()
        setMessage(`❌ ${data.detail || 'Failed to update schedule'}`)
      }
    } catch (err) {
      setMessage('❌ Error updating schedule')
    } finally {
      setLoading(false)
      setTimeout(() => setMessage(''), 5000)
    }
  }

  return (
    <div className="schedule-config">
      <div className="schedule-header">
        <h2>⏰ Schedule Management</h2>
        <p>Manage daily schedules and playlist deliveries</p>
      </div>

      {/* Section Tabs */}
      <div className="section-tabs">
        <button
          className={`section-tab ${activeSection === 'simple' ? 'active' : ''}`}
          onClick={() => setActiveSection('simple')}
        >
          <span className="tab-icon">⏰</span>
          <span>Daily Schedule</span>
        </button>
        <button
          className={`section-tab ${activeSection === 'playlists' ? 'active' : ''}`}
          onClick={() => setActiveSection('playlists')}
        >
          <span className="tab-icon">📚</span>
          <span>Playlists</span>
        </button>
        <button
          className={`section-tab ${activeSection === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveSection('documents')}
        >
          <span className="tab-icon">📁</span>
          <span>Documents</span>
        </button>
      </div>

      {/* Simple Daily Schedule Section */}
      {activeSection === 'simple' && (
        <>
          <div className="schedule-card">
            <div className="schedule-toggle">
              <div className="toggle-info">
                <h3>Enable Automation</h3>
                <p>Automatically send daily messages at scheduled time</p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className={`schedule-time ${!enabled ? 'disabled' : ''}`}>
              <div className="time-info">
                <h3>Daily Send Time</h3>
                <p>Messages will be sent at this time every day</p>
              </div>
              <input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                disabled={!enabled}
                className="time-input"
              />
            </div>

            <div className="schedule-preview">
              <div className="preview-icon">📅</div>
              <div className="preview-text">
                {enabled ? (
                  <>
                    <strong>Next send:</strong> Today at {time}
                    <br />
                    <small>Messages will be sent daily at this time</small>
                  </>
                ) : (
                  <>
                    <strong>Automation disabled</strong>
                    <br />
                    <small>Use "Send Now" button for manual sends</small>
                  </>
                )}
              </div>
            </div>

            {message && (
              <div className={`schedule-message ${message.includes('✅') ? 'success' : 'error'}`}>
                {message}
              </div>
            )}

            <button
              onClick={handleSave}
              disabled={loading}
              className="save-button"
            >
              {loading ? '⏳ Saving...' : '💾 Save Schedule'}
            </button>
          </div>

          <div className="schedule-info">
            <h3>📝 How It Works</h3>
            <ul>
              <li>
                <span className="info-icon">1️⃣</span>
                <span>Enable automation and set your preferred time</span>
              </li>
              <li>
                <span className="info-icon">2️⃣</span>
                <span>System will automatically send messages daily</span>
              </li>
              <li>
                <span className="info-icon">3️⃣</span>
                <span>Receive Telegram notifications at scheduled time</span>
              </li>
              <li>
                <span className="info-icon">4️⃣</span>
                <span>Track your progress and maintain your streak!</span>
              </li>
            </ul>
          </div>

          <div className="schedule-tips">
            <h3>💡 Tips</h3>
            <div className="tips-grid">
              <div className="tip-card">
                <span className="tip-icon">🌅</span>
                <h4>Morning Study</h4>
                <p>Set time between 6-8 AM for fresh mind</p>
              </div>
              <div className="tip-card">
                <span className="tip-icon">🌙</span>
                <h4>Evening Review</h4>
                <p>Set time between 8-10 PM for revision</p>
              </div>
              <div className="tip-card">
                <span className="tip-icon">⏰</span>
                <h4>Consistency</h4>
                <p>Same time daily builds discipline</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Playlists Section */}
      {activeSection === 'playlists' && (
        <PlaylistManager chatId={null} />
      )}

      {/* Documents Section */}
      {activeSection === 'documents' && (
        <FileLibrary chatId={null} authToken={authToken} />
      )}
    </div>
  )
}

export default ScheduleConfig
