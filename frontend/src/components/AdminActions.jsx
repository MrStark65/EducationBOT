import { useState, useEffect } from 'react'
import './AdminActions.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function AdminActions({ onAction, chatId }) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [allUsers, setAllUsers] = useState([])

  useEffect(() => {
    fetchAllUsers()
  }, [])

  const fetchAllUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/users`)
      if (res.ok) {
        const data = await res.json()
        setAllUsers(data.users || [])
      }
    } catch (err) {
      console.error('Error fetching users:', err)
    }
  }

  const handleSendNow = async () => {
    if (loading) return
    
    setLoading(true)
    setMessage('')
    
    try {
      // Send to ALL users
      const results = []
      for (const user of allUsers) {
        try {
          const res = await fetch(`${API_BASE_URL}/api/admin/send-now?chat_id=${user.chat_id}`, {
            method: 'POST'
          })
          
          const data = await res.json()
          
          if (res.ok) {
            results.push({ user: user.first_name, success: true, day: data.day })
          } else {
            // Handle "already sent today" as a partial success
            if (data.detail && data.detail.includes('Already sent today')) {
              results.push({ user: user.first_name, success: true, alreadySent: true })
            } else {
              results.push({ user: user.first_name, success: false, error: data.detail })
            }
          }
        } catch (err) {
          results.push({ user: user.first_name, success: false, error: 'Network error' })
        }
      }
      
      // Show detailed summary
      const successCount = results.filter(r => r.success && !r.alreadySent).length
      const alreadySentCount = results.filter(r => r.alreadySent).length
      const failCount = results.filter(r => !r.success).length
      
      if (failCount === 0 && alreadySentCount === 0) {
        setMessage(`✅ Successfully sent to all ${successCount} users!`)
      } else if (failCount === 0 && successCount === 0) {
        setMessage(`ℹ️ All ${alreadySentCount} users already received today's message`)
      } else if (failCount === 0) {
        setMessage(`✅ Sent to ${successCount} users, ${alreadySentCount} already received today`)
      } else {
        setMessage(`⚠️ Sent: ${successCount}, Already sent: ${alreadySentCount}, Failed: ${failCount}`)
      }
      
      if (onAction) onAction()
    } catch (err) {
      setMessage('❌ Error sending messages')
    } finally {
      setLoading(false)
      setTimeout(() => setMessage(''), 8000) // Longer timeout for detailed message
    }
  }

  const handleReset = async () => {
    if (loading) return
    
    const confirmed = window.confirm(
      '⚠️ Are you sure you want to reset ALL progress?\n\nThis will:\n- Reset all video indices to 0\n- Clear all daily logs\n- Reset streak to 0\n- Reset day count to 0\n\nThis action cannot be undone!'
    )
    
    if (!confirmed) return
    
    setLoading(true)
    setMessage('')
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/reset?chat_id=${chatId}`, {
        method: 'POST'
      })
      
      if (res.ok) {
        setMessage('✅ Progress reset successfully!')
        if (onAction) onAction()
      } else {
        setMessage('❌ Failed to reset progress')
      }
    } catch (err) {
      setMessage('❌ Error resetting progress')
    } finally {
      setLoading(false)
      setTimeout(() => setMessage(''), 5000)
    }
  }

  return (
    <div className="admin-actions">
      <h2>🔧 Admin Actions</h2>
      {message && <div className="action-message">{message}</div>}
      <div className="action-buttons">
        <button
          onClick={handleSendNow}
          disabled={loading || allUsers.length === 0}
          className="btn-action btn-send"
        >
          {loading ? '⏳ Sending...' : `📤 Send to All Users (${allUsers.length})`}
        </button>
        <button
          onClick={handleReset}
          disabled={loading}
          className="btn-action btn-reset"
        >
          {loading ? '⏳ Resetting...' : '🔄 Reset Current User'}
        </button>
      </div>
    </div>
  )
}

export default AdminActions
