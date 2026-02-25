import { useState, useEffect } from 'react'
import './ConfigPanel.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function ConfigPanel({ onUpdate, chatId }) {
  const [playlists, setPlaylists] = useState({})
  const [editing, setEditing] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (chatId) {
      fetchPlaylists()
    }
  }, [chatId])

  const fetchPlaylists = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/config/playlists?chat_id=${chatId}`)
      if (!res.ok) {
        console.error('Failed to fetch playlists:', res.status)
        return
      }
      const data = await res.json()
      setPlaylists(data)
    } catch (err) {
      console.error('Error fetching playlists:', err)
    }
  }

  const handleEdit = (subject) => {
    setEditing(subject)
    setEditValue(playlists[subject] || '')
    setError('')
  }

  const handleSave = async (subject) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/config/playlists?chat_id=${chatId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, url: editValue })
      })

      if (!res.ok) {
        const data = await res.json()
        setError(data.detail || 'Failed to update playlist')
        return
      }

      setEditing(null)
      setError('')
      await fetchPlaylists()
      if (onUpdate) onUpdate()
    } catch (err) {
      setError('Failed to update playlist')
    }
  }

  const handleCancel = () => {
    setEditing(null)
    setEditValue('')
    setError('')
  }

  const subjects = ['english', 'history', 'polity', 'geography', 'economics']

  return (
    <div className="config-panel">
      <h2>⚙️ Playlist Configuration</h2>
      {error && <div className="error-message">{error}</div>}
      <div className="playlist-list">
        {subjects.map((subject) => (
          <div key={subject} className="playlist-item">
            <label>{subject.charAt(0).toUpperCase() + subject.slice(1)}</label>
            {editing === subject ? (
              <div className="edit-mode">
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  placeholder="YouTube playlist URL"
                />
                <div className="edit-actions">
                  <button onClick={() => handleSave(subject)} className="btn-save">
                    Save
                  </button>
                  <button onClick={handleCancel} className="btn-cancel">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="view-mode">
                <span className="playlist-url">{playlists[subject] || 'Not set'}</span>
                <button onClick={() => handleEdit(subject)} className="btn-edit">
                  Edit
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ConfigPanel
