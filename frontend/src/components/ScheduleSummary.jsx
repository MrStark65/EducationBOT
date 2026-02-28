import { useState, useEffect } from 'react'
import './ScheduleSummary.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function ScheduleSummary({ token }) {
  const [scheduleData, setScheduleData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchScheduleSummary()
  }, [])

  const fetchScheduleSummary = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/config/schedule-summary`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch schedule summary')
      }

      const data = await response.json()
      setScheduleData(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching schedule summary:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getSubjectEmoji = (subject) => {
    const emojiMap = {
      'english': '🗣️',
      'history': '🏛️',
      'polity': '⚖️',
      'geography': '🌍',
      'economics': '💰'
    }
    return emojiMap[subject] || '📚'
  }

  if (loading) {
    return (
      <div className="schedule-summary-container">
        <div className="loading">Loading schedule...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="schedule-summary-container">
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  if (!scheduleData) {
    return null
  }

  const todaySchedule = scheduleData.weekly_schedule.find(day => day.is_today)

  return (
    <div className="schedule-summary-container">
      <div className="schedule-header">
        <h2>📅 Schedule Overview</h2>
        <div className="schedule-status">
          <span className={`status-badge ${scheduleData.schedule_enabled ? 'enabled' : 'disabled'}`}>
            {scheduleData.schedule_enabled ? '✅ Enabled' : '⏸️ Disabled'}
          </span>
          <span className="schedule-time">⏰ Send Time: {scheduleData.schedule_time}</span>
          <span className="current-day">📍 Day {scheduleData.current_day}</span>
        </div>
      </div>

      {/* Today's Schedule Highlight */}
      {todaySchedule && (
        <div className="today-schedule-card">
          <h3>📆 Today's Schedule ({todaySchedule.day_name})</h3>
          <div className="subjects-list">
            {todaySchedule.subjects.length > 0 ? (
              todaySchedule.subjects.map((subject, index) => (
                <div key={index} className="subject-badge">
                  {getSubjectEmoji(subject)} {subject.charAt(0).toUpperCase() + subject.slice(1)}
                </div>
              ))
            ) : (
              <div className="no-subjects">⏭️ No subjects scheduled for today</div>
            )}
          </div>
        </div>
      )}

      {/* Weekly Calendar View */}
      <div className="weekly-calendar">
        <h3>📅 Weekly Schedule</h3>
        <div className="calendar-grid">
          {scheduleData.weekly_schedule.map((day, index) => (
            <div 
              key={index} 
              className={`calendar-day ${day.is_today ? 'today' : ''}`}
            >
              <div className="day-header">
                <span className="day-name">{day.day_name}</span>
                {day.is_today && <span className="today-badge">Today</span>}
              </div>
              <div className="day-subjects">
                {day.subjects.length > 0 ? (
                  day.subjects.map((subject, idx) => (
                    <div key={idx} className="subject-item">
                      <span className="subject-emoji">{getSubjectEmoji(subject)}</span>
                      <span className="subject-name">{subject.charAt(0).toUpperCase() + subject.slice(1)}</span>
                    </div>
                  ))
                ) : (
                  <div className="no-subjects-small">⏭️ Rest day</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="schedule-footer">
        <button onClick={fetchScheduleSummary} className="refresh-button">
          🔄 Refresh Schedule
        </button>
      </div>
    </div>
  )
}

export default ScheduleSummary
