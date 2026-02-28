import { useState, useEffect } from 'react'
import './PlaylistStatus.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function PlaylistStatus({ token }) {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resetting, setResetting] = useState(null)

  useEffect(() => {
    fetchStatus()
    // Refresh every 5 minutes
    const interval = setInterval(fetchStatus, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/playlists/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch playlist status')
      }

      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching playlist status:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async (subject) => {
    if (!confirm(`Reset ${subject} playlist to beginning? This will restart from video #1.`)) {
      return
    }

    try {
      setResetting(subject)
      const response = await fetch(`${API_BASE_URL}/api/playlists/${subject}/reset`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to reset playlist')
      }

      // Refresh status
      await fetchStatus()
      alert(`✅ ${subject} playlist reset successfully!`)
    } catch (err) {
      console.error('Error resetting playlist:', err)
      alert(`❌ Failed to reset playlist: ${err.message}`)
    } finally {
      setResetting(null)
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

  const getStatusColor = (percentage) => {
    if (percentage >= 90) return 'danger'
    if (percentage >= 70) return 'warning'
    return 'success'
  }

  if (loading && !status) {
    return (
      <div className="playlist-status-container">
        <div className="loading">Loading playlist status...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="playlist-status-container">
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  if (!status) {
    return null
  }

  const completedPlaylists = status.playlists.filter(p => p.is_completed)
  const hasWarnings = status.playlists.some(p => p.completion_percentage >= 70)

  return (
    <div className="playlist-status-container">
      <div className="status-header">
        <h2>📊 Playlist Progress</h2>
        <button onClick={fetchStatus} className="refresh-button" disabled={loading}>
          {loading ? '⏳' : '🔄'} Refresh
        </button>
      </div>

      {!status.youtube_api_configured && (
        <div className="info-banner">
          💡 Add YOUTUBE_API_KEY to .env for accurate playlist lengths
        </div>
      )}

      {completedPlaylists.length > 0 && (
        <div className="alert-banner completed">
          ⚠️ {completedPlaylists.length} playlist(s) completed! Reset or update playlist URLs.
        </div>
      )}

      {hasWarnings && !completedPlaylists.length && (
        <div className="alert-banner warning">
          ⚠️ Some playlists are nearing completion. Plan ahead!
        </div>
      )}

      <div className="playlists-grid">
        {status.playlists.map((playlist) => (
          <div 
            key={playlist.subject} 
            className={`playlist-card ${playlist.is_completed ? 'completed' : ''}`}
          >
            <div className="playlist-card-header">
              <div className="subject-info">
                <span className="subject-emoji">{getSubjectEmoji(playlist.subject)}</span>
                <h3>{playlist.subject.charAt(0).toUpperCase() + playlist.subject.slice(1)}</h3>
              </div>
              {playlist.is_completed && (
                <span className="completed-badge">✅ Completed</span>
              )}
            </div>

            <div className="progress-info">
              <div className="progress-stats">
                <div className="stat">
                  <span className="stat-label">Current</span>
                  <span className="stat-value">#{playlist.current_index}</span>
                </div>
                {playlist.total_videos && (
                  <>
                    <div className="stat">
                      <span className="stat-label">Total</span>
                      <span className="stat-value">{playlist.total_videos}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Remaining</span>
                      <span className="stat-value">{playlist.remaining_videos}</span>
                    </div>
                  </>
                )}
              </div>

              {playlist.completion_percentage !== null && (
                <div className="progress-bar-container">
                  <div 
                    className={`progress-bar ${getStatusColor(playlist.completion_percentage)}`}
                    style={{ width: `${playlist.completion_percentage}%` }}
                  >
                    <span className="progress-text">{playlist.completion_percentage}%</span>
                  </div>
                </div>
              )}

              {playlist.total_videos === null && (
                <div className="unknown-length">
                  📊 Playlist length unknown
                </div>
              )}
            </div>

            {playlist.is_completed && (
              <button
                onClick={() => handleReset(playlist.subject)}
                disabled={resetting === playlist.subject}
                className="reset-button"
              >
                {resetting === playlist.subject ? '⏳ Resetting...' : '🔄 Reset to Beginning'}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default PlaylistStatus
