import './MetricsPanel.css'

function MetricsPanel({ metrics }) {
  if (!metrics) return null

  return (
    <div className="metrics-panel">
      <div className="metric-card">
        <div className="metric-icon">📅</div>
        <div className="metric-content">
          <div className="metric-label">Current Day</div>
          <div className="metric-value">{metrics.current_day}</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon">📊</div>
        <div className="metric-content">
          <div className="metric-label">Overall Completion</div>
          <div className="metric-value">{metrics.overall_completion}%</div>
          <div className="metric-sub">{metrics.completed_days}/{metrics.total_days} days</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon">📈</div>
        <div className="metric-content">
          <div className="metric-label">Weekly Completion</div>
          <div className="metric-value">{metrics.weekly_completion}%</div>
          <div className="metric-sub">Last 7 days</div>
        </div>
      </div>

      <div className="metric-card streak">
        <div className="metric-icon">🔥</div>
        <div className="metric-content">
          <div className="metric-label">Study Streak</div>
          <div className="metric-value">{metrics.streak}</div>
          <div className="metric-sub">consecutive days</div>
        </div>
      </div>
    </div>
  )
}

export default MetricsPanel
