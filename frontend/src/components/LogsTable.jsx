import './LogsTable.css'

function LogsTable({ logs }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'DONE':
        return '✅'
      case 'NOT_DONE':
        return '❌'
      case 'PENDING':
        return '⏳'
      default:
        return '❓'
    }
  }

  const getStatusClass = (status) => {
    return `status-${status.toLowerCase()}`
  }

  return (
    <div className="logs-section">
      <h2>📋 Daily Study Log</h2>
      <div className="table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Date</th>
              <th>English #</th>
              <th>GK Subject</th>
              <th>GK #</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan="6" className="empty-state">
                  No study logs yet. Start your journey!
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td className="day-cell">{log.day_number}</td>
                  <td>{log.date}</td>
                  <td>{log.english_video_number}</td>
                  <td className="subject-cell">{log.gk_subject}</td>
                  <td>{log.gk_video_number}</td>
                  <td className={`status-cell ${getStatusClass(log.status)}`}>
                    <span className="status-badge">
                      {getStatusIcon(log.status)} {log.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default LogsTable
