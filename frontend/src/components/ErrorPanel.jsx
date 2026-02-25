import { useState, useEffect } from 'react'
import './ErrorPanel.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function ErrorPanel() {
  const [errors, setErrors] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchErrors()
  }, [])

  const fetchErrors = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/errors/recent?limit=10`)
      const data = await res.json()
      setErrors(data.errors || [])
      setLoading(false)
    } catch (err) {
      console.error('Error fetching errors:', err)
      setLoading(false)
    }
  }

  if (loading) return null
  if (errors.length === 0) return null

  return (
    <div className="error-panel">
      <h2>⚠️ Recent Errors</h2>
      <div className="error-list">
        {errors.map((error) => (
          <div key={error.id} className="error-item">
            <div className="error-header">
              <span className="error-type">{error.error_type}</span>
              <span className="error-time">{new Date(error.timestamp).toLocaleString()}</span>
            </div>
            <div className="error-message">{error.error_message}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ErrorPanel
